# OpenClaw Skills Collection for Huawei Cloud L Instance

[中文版 README](README_CN.md)

## Introduction

This repository provides a comprehensive skill adaptation solution for Huawei Cloud L instances, integrating 13 skills across 7 high-frequency practical scenarios. It covers multi-dimensional needs including automated development, operations & promotion, office efficiency, data processing, and compliance review. All skills can be deployed directly on Huawei Cloud L instances for rapid invocation and efficient operations.

The skill collection focuses on scenario-based implementation for Huawei Cloud L instances. It requires no complex configuration and works out of the box, helping users quickly unlock the value of their instances and reduce operational costs across multiple scenarios. It is suitable for the core needs of diverse user groups including individual developers, enterprise office workers, and operations personnel.

### Core Capabilities

-   💻 **Automated Development Assistant**: Focuses on backend development, code generation, test writing, and GitHub automation.
-   📱 **Xiaohongshu Operations Assistant**: Hotspot discovery, competitor research, content creation, image generation, and publishing scheduling.
-   📊 **Daily Hotspot Tracker**: Monitors tech & digital hotspots on platforms like Weibo and Zhihu, automatically generates content drafts, and sends QQ reminders.
-   ✅ **One-Stop Ad Content Compliance Audit**: Automates image OCR, prohibited word detection under advertising laws, and platform rule review, outputting a unified compliance report.
-   📦 **POSpal Inventory Automated Sync Tool**: A secure and reliable tool for automating POSpal inventory management, supporting environment variable configuration and batch operations.
-   📝 **Teacher Assistant**: Assists with student performance management, data analysis, report generation, and home-school communication.
-   🔍 **Log Analysis**: Analyzes daily error logs, diagnoses issues, provides solutions, and archives knowledge.

## Installation

> Coming soon: A complete installation script will be provided later, supporting one-click deployment on Huawei Cloud L instances, including the entire process of dependency installation and environment configuration.

## Skill List

| Skill | Description |
| :--- | :--- |
| `github-auth` | GitHub authentication configuration. Sets up SSH keys or personal access tokens for remote operations. Activated when users need to configure GitHub access. |
| `github-remote` | GitHub remote operations. Supports cloning, pushing, branch creation, PR creation, Issue management, and Release creation. Activated when users need to interact with GitHub repositories. |
| `huawei-image-gen` | Generates images using the Qwen-image model on the Huawei Cloud MaaS platform. |
| `xhs-image-advisor` | Image solution generation for Xiaohongshu posts. Develops image strategies based on content and account style, generates 8-dimensional prompts, and calls `huawei-image-gen` to create images. |
| `xhs-researcher` | Competitor research tool. Conducts content angle research using Sogou WeChat Search, analyzes competitors through comprehensive web searches, refines differentiation angles, and provides data support for topic selection. |
| `xhs-scheduler` | Xiaohongshu smart scheduling publisher. Helps content creators automate content scheduling and timed publishing. |
| `xhs-trending` | Multi-platform hotspot fetcher. Filters hotspots relevant to the Xiaohongshu account's domain and outputs a TOP hotspot list. |
| `xhs-writer` | Xiaohongshu content creation suite. Offline generation of viral titles, body text, hashtags, comments, and multi-image card Markdown, providing comprehensive support for various topics. |
| `daily-hotspot-tracker` | A fully automated tech & digital hotspot monitoring system. Supports multi-platform hotspot discovery, intelligent analysis, content generation, and real-time alerts. |
| `advertising-content-audit` | Provides one-stop compliance audit services for advertising content. |
| `pospal-inventory-sync` | Automates product inventory management for the POSpal system (beta74.pospal.cn), including login, product search, inventory modification, and batch operations. |
| `teacher-assistant` | Teacher assistant skill - a complete home-school communication and student performance management system. Activated when users mention student grades, parent communication, performance analysis, report sending, grade file uploading, or need to generate student reports. |
| `og-analyzer-pro` | Focuses on log analysis, system monitoring, fault diagnosis, and automated operations. |
