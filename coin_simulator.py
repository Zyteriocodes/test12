#!/usr/bin/env python3
"""
Fair (or biased) coin flip simulator with optional batch runs and statistics.
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class FlipStats:
    heads: int = 0
    tails: int = 0

    @property
    def total(self) -> int:
        return self.heads + self.tails

    def record(self, is_heads: bool) -> None:
        if is_heads:
            self.heads += 1
        else:
            self.tails += 1

    def summary(self) -> str:
        if self.total == 0:
            return "No flips yet."
        ph = 100.0 * self.heads / self.total
        pt = 100.0 * self.tails / self.total
        return (
            f"Flips: {self.total} | Heads: {self.heads} ({ph:.2f}%) | "
            f"Tails: {self.tails} ({pt:.2f}%)"
        )


@dataclass
class CoinSimulator:
    """
    probability_heads: float in (0, 1). 0.5 is a fair coin.
    """

    probability_heads: float = 0.5
    rng: random.Random = field(default_factory=random.Random)
    stats: FlipStats = field(default_factory=FlipStats)

    def __post_init__(self) -> None:
        if not 0.0 < self.probability_heads < 1.0:
            raise ValueError("probability_heads must be strictly between 0 and 1")

    def flip(self) -> bool:
        """Return True for heads, False for tails."""
        is_heads = self.rng.random() < self.probability_heads
        self.stats.record(is_heads)
        return is_heads

    def flip_many(self, n: int) -> list[bool]:
        return [self.flip() for _ in range(n)]


def run_interactive(sim: CoinSimulator) -> None:
    print("Coin simulator — commands: [f]lip, [s]tats, [q]uit")
    while True:
        try:
            raw = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if raw in ("q", "quit", "exit"):
            break
        if raw in ("s", "stats"):
            print(sim.stats.summary())
            continue
        if raw in ("f", "flip", "") or raw.isspace():
            side = "Heads" if sim.flip() else "Tails"
            print(f"  {side}")
            continue
        if raw.isdigit():
            n = int(raw)
            if n <= 0:
                print("  Use a positive number of flips.")
                continue
            results = sim.flip_many(n)
            c = Counter("H" if h else "T" for h in results)
            print(f"  {n} flips: H={c['H']} T={c['T']}")
            continue

        print("  Unknown command. Try f, s, a number, or q.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulate coin flips.")
    parser.add_argument(
        "-n",
        "--flips",
        type=int,
        default=None,
        metavar="N",
        help="Run N flips and print summary (non-interactive).",
    )
    parser.add_argument(
        "-p",
        "--p-heads",
        type=float,
        default=0.5,
        help="Probability of heads (default: 0.5, fair coin).",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible runs.",
    )
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    try:
        sim = CoinSimulator(probability_heads=args.p_heads, rng=rng)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    if args.flips is not None:
        if args.flips < 0:
            print("N must be non-negative.", file=sys.stderr)
            return 2
        sim.flip_many(args.flips)
        print(sim.stats.summary())
        return 0

    run_interactive(sim)
    print(sim.stats.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
