#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OrionAgent — Generalized Multi-LLM Agentic Intelligence Framework
Setup configuration for package installation.
"""

import io
from setuptools import setup, find_packages


def read_file(filename: str) -> str:
    with io.open(filename, encoding="utf-8") as f:
        return f.read()


setup(
    # ─── Metadata ────────────────────────────────────────────────────────────
    name="orionagent",
    version="1.0.0",
    python_requires=">=3.10",
    author="OrionAgent Contributors",
    description=(
        "OrionAgent: A production-grade, generalized information-seeking "
        "agent framework powered by Meta-Agent Tuning (MAT) and large language models."
    ),
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/OrionAgent",
    project_urls={
        "Documentation": "https://github.com/your-org/OrionAgent#readme",
        "Bug Tracker":   "https://github.com/your-org/OrionAgent/issues",
        "Research Paper": "https://arxiv.org/abs/2312.04889",
    },

    # ─── Classifiers ─────────────────────────────────────────────────────────
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],

    # ─── Package Discovery ────────────────────────────────────────────────────
    packages=find_packages(exclude=["tests*", "scripts*", "docs*", "benchmark*"]),
    include_package_data=True,

    # ─── CLI Entry Points ─────────────────────────────────────────────────────
    entry_points={
        "console_scripts": [
            "orionagent=orionagent.agent_start:main",
            # Legacy alias preserved for backward compatibility
            "kagentsys=orionagent.agent_start:main",
        ]
    },

    # ─── Dependencies ─────────────────────────────────────────────────────────
    install_requires=read_file("requirements.txt").strip().splitlines(),

    # ─── License ──────────────────────────────────────────────────────────────
    license="Attribution-NonCommercial-ShareAlike 4.0 International",
)
