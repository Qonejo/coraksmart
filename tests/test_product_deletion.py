import pytest
from app import app, db, Product
import json
import uuid

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    # Use an in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key' # Needed for session

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            # Simulate a logged-in admin user
            with testing_client.session_transaction() as session:
                session['logged_in'] = True
        yield testing_client
        with app.app_context():
            db.drop_all()

def test_delete_product_in_bundle_fails(test_client):
    """
    GIVEN a product that is part of a bundle
    WHEN an admin tries to delete that product via the API
    THEN the product should NOT be deleted and the API should return an error
    """
    # 1. Setup: Create products and a bundle
    with app.app_context():
        # Create a product that will be part of the bundle
        product_id_in_bundle = str(uuid.uuid4())
        p_in_bundle = Product(id=product_id_in_bundle, nombre="Special Chocolate", precio=5.0)
        db.session.add(p_in_bundle)
        db.session.commit()

        # Create a bundle containing the product
        bundle_id = str(uuid.uuid4())
        bundle = Product(
            id=bundle_id,
            nombre="Sweet Deal Bundle",
            precio=10.0,
            bundle_items=json.dumps([product_id_in_bundle]) # The bug is related to this
        )
        db.session.add(bundle)
        db.session.commit()

        assert Product.query.get(product_id_in_bundle) is not None

    # 2. Action: Try to delete the product that is in the bundle
    response = test_client.post(f'/admin/eliminar-producto/{product_id_in_bundle}')

    # 3. Assert: Check that the API response indicates failure
    # This assertion will fail initially because the current code allows deletion
    assert response.status_code == 400 # Bad Request
    response_data = json.loads(response.data)
    assert response_data['success'] is False
    assert 'no puede ser eliminado porque es parte de los siguientes bundles' in response_data['message']
    assert 'Sweet Deal Bundle' in response_data['message']

    # And verify the product still exists in the database
    with app.app_context():
        product_still_exists = Product.query.get(product_id_in_bundle)
        assert product_still_exists is not None
