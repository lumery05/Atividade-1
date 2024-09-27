import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from trabalho import app, db, Item
class FlaskTestCase(unittest.TestCase):
    # Configuração inicial do ambiente de teste
    def setUp(self):
        # Configurando o app para o modo de teste
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco de dados em memória para testes
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    # Cleanup após cada teste
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Testar se a página inicial carrega corretamente
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CRUD App', response.data)

    # Testar adição de novo item
    def test_add_item(self):
        response = self.app.post('/add', data={'name': 'Item Teste'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item Teste', response.data)

        # Verificar se o item foi adicionado ao banco de dados
        item = Item.query.filter_by(name='Item Teste').first()
        self.assertIsNotNone(item)

    # Testar atualização de item
    def test_update_item(self):
        # Adicionando item
        item = Item(name='Item Antigo')
        db.session.add(item)
        db.session.commit()

        # Atualizando o item
        response = self.app.post(f'/update/{item.id}', data={'name': 'Item Atualizado'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item Atualizado', response.data)

        # Verificar se o item foi atualizado no banco de dados
        updated_item = db.session.get(Item, item.id)
        self.assertEqual(updated_item.name, 'Item Atualizado')

    # Testar exclusão de item
    def test_delete_item(self):
        # Adicionando item
        item = Item(name='Item a ser Deletado')
        db.session.add(item)
        db.session.commit()

        # Deletando o item
        response = self.app.get(f'/delete/{item.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Item a ser Deletado', response.data)

        # Verificar se o item foi removido do banco de dados
        deleted_item = db.session.get(Item, item.id)
        self.assertIsNone(deleted_item)

if __name__ == '__main__':
    unittest.main()
