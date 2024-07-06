#!/usr/bin/env python3
"""test_auth."""
import unittest
from flask_testing import TestCase
from app import create_app, db
from models.user import User


class BaseTestCase(TestCase):
    """Base test case."""

    def create_app(self):
        """Create app."""
        app = create_app('config.TestConfig')
        return app

    def setUp(self):
        """Set up integration test."""
        db.create_all()

    def tearDown(self):
        """Tear down integration test."""
        db.session.remove()
        db.drop_all()


class TestAuth(BaseTestCase):
    """Test auth."""

    def test_register_success(self):
        """Test register success."""
        response = self.client.post('/auth/register', json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password",
            "phone": "1234567890"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['user']['firstName'], 'John')

    def test_register_missing_fields(self):
        """Test register missing fields."""
        response = self.client.post('/auth/register', json={
            "firstName": "John",
            "email": "john@example.com",
            "password": "password",
        })
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertGreater(len(data['errors']), 0)

    def test_register_duplicate_email(self):
        """Test register duplicate email."""
        self.client.post('/auth/register', json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password",
            "phone": "1234567890"
        })
        response = self.client.post('/auth/register', json={
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password",
            "phone": "0987654321"
        })
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertTrue(
            any(error['field'] == 'email' for error in data['errors']))

    def test_login_success(self):
        """Test login success."""
        self.client.post('/auth/register', json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password",
            "phone": "1234567890"
        })
        response = self.client.post('/auth/login', json={
            "email": "john@example.com",
            "password": "password"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('accessToken', data['data'])

    def test_login_failure(self):
        """Test login failure."""
        self.client.post('/auth/register', json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "password",
            "phone": "1234567890"
        })
        response = self.client.post('/auth/login', json={
            "email": "john@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['status'], 'Bad request')
        self.assertEqual(data['message'], 'Authentication failed')


if __name__ == '__main__':
    unittest.main()
