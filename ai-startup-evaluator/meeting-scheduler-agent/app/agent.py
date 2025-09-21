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

def schedule_meeting(founder_name: str, preferred_time: str) -> str:
    """Schedule a meeting with the founder"""
    return f"Scheduled meeting for {founder_name} at {preferred_time}"

def check_availability(time_slot: str) -> str:
    """Check availability for a time slot"""
    return f"Availability checked for: {time_slot}"

def send_invitations(meeting_details: str) -> str:
    """Send meeting invitations"""
    return f"Invitations sent for: {meeting_details}"

# Create the agent
root_agent = Agent(
    name="meeting_scheduler_agent",
    model="gemini-2.5-flash",
    instruction="Meeting Scheduler Agent - Intelligent meeting scheduling",
    tools=[schedule_meeting, check_availability, send_invitations],
)
