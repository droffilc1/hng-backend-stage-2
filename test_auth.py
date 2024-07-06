#!/usr/bin/env python3
"""Unit tests."""
import unittest
from app import app, db, User, Organisation
from flask_testing import TestCase


class BaseTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestAuth(BaseTestCase):
    def test_register_success(self):
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
        response = self.client.post('/auth/register', json={
            "firstName": "John",
            "email": "john@example.com",
            "password": "password",
        })
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertGreater(len(data['errors']), 0)

    def test_register_duplicate_email(self):
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
