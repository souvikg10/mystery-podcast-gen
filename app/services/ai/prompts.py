"""prompts module."""
"""
AI prompts for different content categories.
"""
from app.models.content import ContentCategory

# Dictionary of prompts for different content categories
CATEGORY_PROMPTS = {
    ContentCategory.RESEARCH: """
    Transform this research paper into a thrilling true crime narrative podcast.
    Frame the research problem as a mystery, methods as investigation techniques,
    and findings as dramatic revelations. Use dramatic tension and create suspense
    around the research outcomes.
    The conversation is happening between two speakers. Focus only on what they will say
    No additional sound cues. 
    
    Style Guidelines:
    - Present the research question as an unsolved mystery
    - Turn methodology into detective work
    - Frame data analysis as uncovering evidence
    - Present findings as breakthrough revelations
    - Return transcript as Speaker 1: or Speaker 2: and each line is a sentence the speaker is going to say
    

    Original content:
    {content}
    """,
    
    ContentCategory.TECHNICAL: """
    Transform this technical documentation into a conspiracy theory style podcast script.
    Present the technical concepts as hidden knowledge being revealed, with connections
    and patterns that "they don't want you to know about."
    The conversation is happening between two speakers. Focus only on what they will say
    No additional sound cues.
    
    Style Guidelines:
    - Frame technical concepts as "hidden knowledge"
    - Present features as "secret capabilities"
    - Connect different parts of the documentation in unexpected ways
    - Use phrases like "But here's what they're not telling you..."
    - Return transcript as Speaker 1: or Speaker 2: and each line is a sentence the speaker is going to say
    
    
    Original content:
    {content}
    """
}

# Content summary prompt
CONTENT_SUMMARY_PROMPT = """
Analyze and synthesize the following content into a coherent narrative.
Each document is separated by '=== Next Document ==='.
Find connections between the documents and create a unified story.
Make it clear and engaging while preserving the key information from each source.

Content to analyze:
{content}
"""

# Transcript refinement prompt
TRANSCRIPT_REFINEMENT_PROMPT = """
Refine the following podcast transcript according to these notes while keeping 
the core content and information intact. Maintain the same two-speaker format 
and dramatic elements, but adjust the style and presentation as requested.

Original Transcript:
{transcript}

Refinement Notes:
{notes}

Keep the format:
**Speaker 1:** dialogue
**Speaker 2:** dialogue

Make sure to:
1. Keep all important information from the original
2. Maintain the conversational flow
3. Apply the requested style changes
4. Keep dramatic elements and tone indicators
5. Preserve the alternating speaker format
"""