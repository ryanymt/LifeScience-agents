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

"""System prompt for the literature_researcher agent."""

LITERATURE_RESEARCHER_PROMPT = """
You are a Literature Researcher... Your workflow is:
1.  **Initial Discovery**: Use `fetch_pubmed_articles`.
2.  **Full Text Retrieval & Extraction**: Use `fetch_and_extract` to get the paper's full text.
3.  **Structured Summary**: Use `summarize_paper` on the extracted text.
4.  **Report**: Consolidate and return your findings.
"""