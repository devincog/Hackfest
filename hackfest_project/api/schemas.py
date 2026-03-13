"""
Pydantic schemas for the slide_schema JSON structure.
These define the SHAPE of the LLM's output — not the content.
The LLM dynamically fills in titles, bullets, animations, etc.
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AnimationType(str, Enum):
    FADE_IN = "fade-in"
    FADE_UP = "fade-up"
    FADE_DOWN = "fade-down"
    FADE_LEFT = "fade-left"
    FADE_RIGHT = "fade-right"
    ZOOM_IN = "zoom-in"
    SLIDE_IN = "slide-in"
    NONE = "none"


class TransitionType(str, Enum):
    SLIDE = "slide"
    FADE = "fade"
    CONVEX = "convex"
    CONCAVE = "concave"
    ZOOM = "zoom"
    NONE = "none"


class SlideElement(BaseModel):
    """A single content element on a slide (bullet, text, image placeholder)."""
    type: str = Field(description="Element type: 'heading', 'bullet', 'text', 'image_placeholder', 'quote'")
    content: str = Field(description="The text content of this element")
    animation: AnimationType = Field(default=AnimationType.FADE_IN, description="Animation for this element")
    animation_delay: float = Field(default=0.0, description="Delay in seconds before animation starts")
    source_chunk: Optional[str] = Field(default=None, description="Reference to source document chunk")


class Slide(BaseModel):
    """A single slide in the presentation."""
    slide_number: int
    title: str
    elements: list[SlideElement] = Field(default_factory=list)
    transition: TransitionType = Field(default=TransitionType.SLIDE)
    background_color: Optional[str] = Field(default=None, description="CSS color value e.g. '#1a1a2e'")
    speaker_notes: Optional[str] = Field(default=None)


class SlideDeck(BaseModel):
    """The complete presentation schema."""
    title: str = Field(description="Overall presentation title")
    subtitle: Optional[str] = Field(default=None)
    theme: str = Field(default="dark", description="Reveal.js theme: 'dark', 'light', 'night', etc.")
    slides: list[Slide] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list, description="List of referenced source documents")
