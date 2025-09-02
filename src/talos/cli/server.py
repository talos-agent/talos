#!/usr/bin/env python3
"""
Simple REST API server for testing purposes.
Runs on port 8000 with basic CRUD endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

# In-memory storage for testing
items_db: List[Dict] = []
next_id = 1

app = FastAPI(
    title="Talos Test API",
    description="A simple REST API for testing purposes",
    version="1.0.0",
)


class ItemCreate(BaseModel):
    """Model for creating a new item."""
    name: str
    description: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ItemUpdate(BaseModel):
    """Model for updating an existing item."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Item(BaseModel):
    """Model for item response."""
    id: int
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "Talos Test API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/items", response_model=List[Item])
async def get_items() -> List[Item]:
    """Get all items."""
    return [Item.model_validate(item) for item in items_db]


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """Get a specific item by ID."""
    for item in items_db:
        if item["id"] == item_id:
            return Item.model_validate(item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate) -> Item:
    """Create a new item."""
    global next_id

    new_item = {
        "id": next_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    items_db.append(new_item)
    next_id += 1

    return Item.model_validate(new_item)


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate) -> Item:
    """Update an existing item."""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            # Update only provided fields
            update_data = item_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                item[key] = value
            item["updated_at"] = datetime.now()

            return Item.model_validate(item)

    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> Dict[str, str]:
    """Delete an item."""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            del items_db[i]
            return {"message": f"Item {item_id} deleted successfully"}

    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items/search/{query}")
async def search_items(query: str) -> List[Item]:
    """Search items by name or description."""
    results = []
    query_lower = query.lower()

    for item in items_db:
        name = str(item["name"])
        description = str(item["description"]) if item["description"] else ""
        if (query_lower in name.lower() or
                (description and query_lower in description.lower())):
            results.append(Item.model_validate(item))

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
