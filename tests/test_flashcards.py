"""Tests for flashcard functionality."""
import pytest
from httpx import AsyncClient

from app.models.user import UserRole


@pytest.mark.asyncio
async def test_create_flashcard_deck(client: AsyncClient, teacher_headers):
    """Test creating a flashcard deck."""
    response = await client.post(
        "/api/v1/flashcards/decks",
        json={
            "name": "Test Physics Deck",
            "description": "Basic physics concepts",
            "subject": "Physics",
            "difficulty": "medium"
        },
        headers=teacher_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Physics Deck"
    assert data["card_count"] == 0


@pytest.mark.asyncio
async def test_create_flashcard(client: AsyncClient, teacher_headers, test_db):
    """Test creating a flashcard."""
    from app.models.flashcard import FlashcardDeck

    # First create a deck
    deck_response = await client.post(
        "/api/v1/flashcards/decks",
        json={
            "name": "Test Deck",
            "description": "Test deck",
            "subject": "Physics",
            "difficulty": "medium"
        },
        headers=teacher_headers
    )
    deck_id = deck_response.json()["id"]

    # Create a card
    response = await client.post(
        "/api/v1/flashcards/cards",
        json={
            "deck_id": deck_id,
            "front": "What is Newton's first law?",
            "back": "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an unbalanced force."
        },
        headers=teacher_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["front"] == "What is Newton's first law?"
    assert data["approved"] is False  # Cards start unapproved


@pytest.mark.asyncio
async def test_get_flashcard_decks(client: AsyncClient, auth_headers):
    """Test retrieving flashcard decks."""
    response = await client.get("/api/v1/flashcards/decks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)