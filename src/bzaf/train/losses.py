"""Training losses on the option scores z and count logits of one batch of rows.

set_nll   −log P(gold set) = −[log P(|S| = s) + Σ_{i∈S} z_i − log e_s(exp z)], exact (elementary symmetric
          polynomials by a log-space dynamic programme over the options). Splits into a count part and a selection part.
choice_ce single-answer rows: cross-entropy of the gold option (the count = 1 case of the same likelihood).
distill   KL(base ‖ model) over the options: keeps the model's answers on general questions close to the base's.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

NEG = -1e4  # stands in for −inf on padded slots, so no gradient becomes NaN


def log_esp(z: torch.Tensor, mask: torch.Tensor, smax: int) -> torch.Tensor:
    """log e_s(exp z) for s = 0..smax over each row's valid options: [B, smax + 1]."""
    z = z.float().masked_fill(~mask, NEG)
    e = torch.full((z.shape[0], smax + 1), -1e30, device=z.device)
    e[:, 0] = 0.0
    for i in range(z.shape[1]):
        e = torch.cat([e[:, :1], torch.logaddexp(e[:, 1:], e[:, :-1] + z[:, i : i + 1])], dim=1)
    return e


def set_nll(scores: torch.Tensor, count_logits: torch.Tensor, gold: torch.Tensor, mask: torch.Tensor) -> dict:
    """Per-row −log P(gold set) and its parts. `gold` is a bool [B, W] mask of correct options."""
    n = gold.sum(-1).clamp(max=count_logits.shape[1] - 1)
    log_c = F.log_softmax(count_logits.float().masked_fill(torch.isinf(count_logits), NEG), -1)
    count_nll = -log_c.gather(1, n[:, None]).squeeze(1)
    z = scores.float().masked_fill(~mask, NEG)
    e = log_esp(z, mask, int(n.max().item()) if n.numel() else 0)
    select_nll = -((z * gold).sum(-1) - e.gather(1, n[:, None]).squeeze(1))
    return {"nll": count_nll + select_nll, "count_nll": count_nll, "select_nll": select_nll}


def choice_ce(scores: torch.Tensor, gold_index: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    z = scores.float().masked_fill(~mask, NEG)
    return F.cross_entropy(z, gold_index, reduction="none")


def distill(scores: torch.Tensor, base_scores: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """KL(p_base ‖ p_model) per row, both softmaxes over the valid options."""
    log_p = F.log_softmax(scores.float().masked_fill(~mask, NEG), -1)
    log_q = F.log_softmax(base_scores.float().masked_fill(~mask, NEG), -1)
    return (log_q.exp() * (log_q - log_p)).masked_fill(~mask, 0.0).sum(-1)
