#!/usr/bin/env/ python3
"""test-organisations."""
import unittest
from flask_testing import TestCase
from flask_jwt_extended import create_access_token
from app import create_app, db
from models import User, Organisation


class BaseTestCase(TestCase):
    """Base test case."""

    def create_app(self):
        """Create app."""
        app = create_app('config.TestConfig')
        return app

    def setUp(self):
        """Set up integration test."""
        db.create_all()
        # Create a sample user
        self.user = User(
            firstName='John',
            lastName='Doe',
            email='john@example.com',
            password='password',
            phone='1234567890'
        )
        db.session.add(self.user)
        db.session.commit()

        # Generate token for the sample user
        self.access_token = create_access_token(identity=self.user.userId)
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def tearDown(self):
        """Tear down integration test."""
        db.session.remove()
        db.drop_all()


class TestOrganisation(BaseTestCase):
    """Test organisation."""

    def test_create_organisation(self):
        """Test create organisation."""
        response = self.client.post('/api/organisations', headers=self.headers, json={
            'name': 'New Organisation',
            'description': 'This is a test organisation'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['name'], 'New Organisation')

    def test_create_organisation_missing_name(self):
        """Test create organisation missing name."""
        response = self.client.post('/api/organisations', headers=self.headers, json={
            'description': 'This is a test organisation'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['status'], 'Bad Request')
        self.assertEqual(data['message'], 'Name is required')

    def test_get_organisations(self):
        """Test get organisation."""
        # Create a sample organisation
        organisation = Organisation(
            name='John\'s Organisation',
            description='This is John\'s default organisation',
            created_by=self.user.userId
        )
        self.user.organisations.append(organisation)
        db.session.commit()

        response = self.client.get('/api/organisations', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['organisations']), 1)

    def test_get_organisation(self):
        """Test get organisation."""
        # Create a sample organisation
        organisation = Organisation(
            name='John\'s Organisation',
            description='This is John\'s default organisation',
            created_by=self.user.userId
        )
        self.user.organisations.append(organisation)
        db.session.commit()

        response = self.client.get(
            f'/api/organisations/{organisation.orgId}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['name'], 'John\'s Organisation')

    def test_get_organisation_not_found(self):
        """Test get organisation not found."""
        response = self.client.get(
            '/api/organisations/invalid_id', headers=self.headers)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['status'], 'Not found')
        self.assertEqual(data['message'], 'Organisation not found')

    def test_add_user_to_organisation(self):
        """Test add user to organisation."""
        # Create a new user to add to the organisation
        new_user = User(
            firstName='Jane',
            lastName='Smith',
            email='jane@example.com',
            password='password',
            phone='0987654321'
        )
        db.session.add(new_user)
        db.session.commit()

        # Create a sample organisation
        organisation = Organisation(
            name='John\'s Organisation',
            description='This is John\'s default organisation',
            created_by=self.user.userId
        )
        self.user.organisations.append(organisation)
        db.session.commit()

        response = self.client.post(f'/api/organisations/{organisation.orgId}/users', headers=self.headers, json={
            'userId': new_user.userId
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(
            data['message'], 'User added to organisation successfully')


if __name__ == '__main__':
    unittest.main()
