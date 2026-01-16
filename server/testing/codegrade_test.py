
import pytest
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, db
from models import Pet


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client


def test_pet_model_exists():
    """Test that Pet model is properly defined"""
    pet = Pet(name="TestPet", species="Dog")
    assert pet.name == "TestPet"
    assert pet.species == "Dog"
    assert pet.id is None


def test_pet_repr():
    """Test Pet model __repr__ method"""
    pet = Pet(name="Fido", species="Dog")
    pet.id = 1
    assert repr(pet) == "<Pet 1, Fido, Dog>"


def test_add_pet(client):
    """Test adding a pet to the database"""
    with app.app_context():
        pet = Pet(name="Fido", species="Dog")
        db.session.add(pet)
        db.session.commit()
        
        # Check the pet was added with an ID
        assert pet.id is not None
        assert pet.name == "Fido"
        assert pet.species == "Dog"
        
        # Query to verify persistence
        fetched_pet = db.session.get(Pet, pet.id)
        assert fetched_pet is not None
        assert fetched_pet.name == "Fido"


def test_query_all_pets(client):
    """Test querying all pets"""
    with app.app_context():
        # Add multiple pets
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.commit()
        
        # Query all pets
        all_pets = Pet.query.all()
        assert len(all_pets) == 2
        assert all_pets[0].name == "Fido"
        assert all_pets[1].name == "Whiskers"


def test_query_first_pet(client):
    """Test querying first pet"""
    with app.app_context():
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.commit()
        
        first_pet = Pet.query.first()
        assert first_pet is not None
        assert first_pet.name == "Fido"


def test_filter_by_species(client):
    """Test filtering pets by species"""
    with app.app_context():
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        pet3 = Pet(name="Buddy", species="Dog")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.add(pet3)
        db.session.commit()
        
        dogs = Pet.query.filter_by(species="Dog").all()
        assert len(dogs) == 2
        for dog in dogs:
            assert dog.species == "Dog"


def test_filter_by_id(client):
    """Test filtering pets by ID"""
    with app.app_context():
        pet = Pet(name="Fido", species="Dog")
        db.session.add(pet)
        db.session.commit()
        
        fetched_pet = Pet.query.filter_by(id=pet.id).first()
        assert fetched_pet is not None
        assert fetched_pet.name == "Fido"


def test_get_pet_by_id(client):
    """Test getting pet by primary key using db.session.get"""
    with app.app_context():
        pet = Pet(name="Fido", species="Dog")
        db.session.add(pet)
        db.session.commit()
        
        fetched_pet = db.session.get(Pet, pet.id)
        assert fetched_pet is not None
        assert fetched_pet.id == pet.id
        assert fetched_pet.name == "Fido"


def test_get_nonexistent_pet(client):
    """Test getting a pet that doesn't exist returns None"""
    with app.app_context():
        pet = db.session.get(Pet, 999)
        assert pet is None


def test_update_pet(client):
    """Test updating a pet's attributes"""
    with app.app_context():
        pet = Pet(name="Fido", species="Dog")
        db.session.add(pet)
        db.session.commit()
        
        # Update the pet's name
        pet.name = "Fido the mighty"
        db.session.commit()
        
        # Verify update persisted
        fetched_pet = db.session.get(Pet, pet.id)
        assert fetched_pet.name == "Fido the mighty"


def test_delete_pet(client):
    """Test deleting a pet from the database"""
    with app.app_context():
        pet = Pet(name="Fido", species="Dog")
        db.session.add(pet)
        db.session.commit()
        pet_id = pet.id
        
        # Delete the pet
        db.session.delete(pet)
        db.session.commit()
        
        # Verify deletion
        fetched_pet = db.session.get(Pet, pet_id)
        assert fetched_pet is None
        
        # Query all should return empty list
        all_pets = Pet.query.all()
        assert len(all_pets) == 0


def test_delete_all_pets(client):
    """Test deleting all pets using query.delete()"""
    with app.app_context():
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.commit()
        
        # Delete all pets
        count = Pet.query.delete()
        db.session.commit()
        
        assert count == 2
        all_pets = Pet.query.all()
        assert len(all_pets) == 0


def test_order_by_species(client):
    """Test ordering pets by species"""
    with app.app_context():
        pet1 = Pet(name="Fido", species="Dog")
        pet2 = Pet(name="Whiskers", species="Cat")
        db.session.add(pet1)
        db.session.add(pet2)
        db.session.commit()
        
        pets = Pet.query.order_by('species').all()
        assert len(pets) == 2
        # Cats should come before Dogs alphabetically
        assert pets[0].species == "Cat"
        assert pets[1].species == "Dog"


def test_flask_app_config():
    """Test Flask app is properly configured"""
    assert app is not None
    assert app.config['SQLALCHEMY_DATABASE_URI'] is not None
    assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
