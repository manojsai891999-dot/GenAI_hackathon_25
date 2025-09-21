# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import logging
from typing import Dict, List, Optional, Any

import google.auth
from google.adk.agents import Agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

logger = logging.getLogger(__name__)

def generate_investment_memo(startup_data: str) -> str:
    """Generate investment memo"""
    return f"Generated investment memo for: {startup_data[:50]}..."

def format_document(memo_content: str) -> str:
    """Format the investment memo document"""
    return f"Formatted memo: {memo_content[:50]}..."

def export_documents(memo: str, format: str) -> str:
    """Export memo in specified format"""
    return f"Exported memo as {format}: {memo[:50]}..."

# Create the agent
root_agent = Agent(
    name="memo_generation_agent",
    model="gemini-2.5-flash",
    instruction="Memo Generation Agent - Investment memo generation agent",
    tools=[generate_investment_memo, format_document, export_documents],
)
