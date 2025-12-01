import { useState, useEffect } from 'react';
import { Dessert, User, ActivityLog } from '../types';
import { dessertsApi, uploadApi, usersApi, logsApi } from '../services/api';
import { getImageUrl } from '../utils/image';
import { useToastContext } from '../contexts/ToastContext';
import ConfirmDialog from './ConfirmDialog';

interface AdminPanelProps {
  onUpdate: () => void;
}

type TabType = 'desserts' | 'users' | 'logs';

export default function AdminPanel({ onUpdate }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>('desserts');
  const [desserts, setDesserts] = useState<Dessert[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingDessert, setEditingDessert] = useState<Dessert | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; type: 'dessert' | 'user' } | null>(null);
  const [editingPriceId, setEditingPriceId] = useState<number | null>(null);
  const [editingPriceValue, setEditingPriceValue] = useState<string>('');
  const [savingPrice, setSavingPrice] = useState(false);
  const { error, success } = useToastContext();

  useEffect(() => {
    loadDesserts();
  }, []);

  const loadDesserts = async () => {
    try {
      setLoading(true);
      const data = await dessertsApi.getAll({ is_active: undefined });
      setDesserts(data);
    } catch (error) {
      console.error('Error loading desserts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (e: React.MouseEvent<HTMLButtonElement>, id: number, type: 'dessert' | 'user' = 'dessert') => {
    e.preventDefault();
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation();
    
    // Additional protection: prevent any default behavior
    if (e.nativeEvent.cancelable) {
      e.nativeEvent.preventDefault();
    }
    
    setDeleteConfirm({ id, type });
    return false;
  };

  const confirmDelete = async (e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!deleteConfirm) return;
    
    const idToDelete = deleteConfirm.id;
    const deleteType = deleteConfirm.type;
    setDeleteConfirm(null); // Закрываем диалог сразу
    
    try {
      if (deleteType === 'dessert') {
        await dessertsApi.delete(idToDelete);
        await loadDesserts();
        onUpdate();
        success('Dessert deleted successfully');
      } else if (deleteType === 'user') {
        await usersApi.delete(idToDelete);
        await loadUsers();
        success('User deleted successfully');
      }
    } catch (err) {
      console.error('Error deleting:', err);
      error(`Error deleting ${deleteType}`);
    }
  };

  const handleEdit = (dessert: Dessert) => {
    setEditingDessert(dessert);
    setShowForm(true);
  };

  const handleCreate = () => {
    setEditingDessert(null);
    setShowForm(true);
  };

  const handlePriceClick = (dessert: Dessert) => {
    setEditingPriceId(dessert.id);
    setEditingPriceValue(dessert.price?.toString() || '');
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditingPriceValue(e.target.value);
  };

  const handlePriceSave = async (dessertId: number) => {
    try {
      setSavingPrice(true);
      const priceValue = editingPriceValue.trim() === '' ? null : parseFloat(editingPriceValue);
      
      if (priceValue !== null && (isNaN(priceValue) || priceValue < 0)) {
        error('Please enter a valid price');
        return;
      }

      await dessertsApi.update(dessertId, { price: priceValue });
      await loadDesserts();
      onUpdate();
      success('Price updated successfully');
      setEditingPriceId(null);
      setEditingPriceValue('');
    } catch (err) {
      console.error('Error updating price:', err);
      error('Error updating price');
    } finally {
      setSavingPrice(false);
    }
  };

  const handlePriceCancel = () => {
    setEditingPriceId(null);
    setEditingPriceValue('');
  };

  const handlePriceKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, dessertId: number) => {
    if (e.key === 'Enter') {
      handlePriceSave(dessertId);
    } else if (e.key === 'Escape') {
      handlePriceCancel();
    }
  };

  if (loading && activeTab === 'desserts') {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      {deleteConfirm && (
        <ConfirmDialog
          title={deleteConfirm.type === 'dessert' ? 'Delete Dessert' : 'Delete User'}
          message={`Are you sure you want to delete this ${deleteConfirm.type}? This action cannot be undone.`}
          confirmText="Delete"
          cancelText="Cancel"
          type="danger"
          onConfirm={(e) => {
            if (e) {
              e.preventDefault();
              e.stopPropagation();
            }
            confirmDelete();
          }}
          onCancel={() => {
            setDeleteConfirm(null);
          }}
        />
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('desserts')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'desserts'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Desserts
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'logs'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Activity Logs
          </button>
        </nav>
      </div>

      {/* Desserts Tab */}
      {activeTab === 'desserts' && (
        <>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Dessert Management</h2>
            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              + Add Dessert
            </button>
          </div>

      {showForm && (
        <DessertForm
          dessert={editingDessert}
          onClose={() => {
            setShowForm(false);
            setEditingDessert(null);
          }}
          onSave={async () => {
            await loadDesserts();
            onUpdate();
            setShowForm(false);
            setEditingDessert(null);
          }}
        />
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200" onContextMenu={(e) => e.preventDefault()}>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Price (THB)
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {desserts.map((dessert) => (
              <tr key={dessert.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{dessert.title}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {dessert.category.split(',').map((cat, idx) => (
                      <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                        {cat.trim()}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      dessert.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {dessert.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {editingPriceId === dessert.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={editingPriceValue}
                        onChange={handlePriceChange}
                        onKeyDown={(e) => handlePriceKeyDown(e, dessert.id)}
                        onBlur={() => handlePriceSave(dessert.id)}
                        autoFocus
                        className="w-24 px-2 py-1 text-sm border border-blue-500 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        disabled={savingPrice}
                      />
                      <button
                        onClick={() => handlePriceSave(dessert.id)}
                        disabled={savingPrice}
                        className="text-green-600 hover:text-green-800 disabled:opacity-50"
                        title="Save"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                      <button
                        onClick={handlePriceCancel}
                        disabled={savingPrice}
                        className="text-red-600 hover:text-red-800 disabled:opacity-50"
                        title="Cancel"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ) : (
                    <div
                      onClick={() => handlePriceClick(dessert)}
                      className="cursor-pointer hover:bg-gray-50 px-2 py-1 rounded transition-colors group"
                      title="Click to edit price"
                    >
                      <span className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                        {dessert.price !== null && dessert.price !== undefined
                          ? `${dessert.price.toFixed(2)} THB`
                          : <span className="text-gray-400 italic">Not set</span>}
                      </span>
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    type="button"
                    onClick={() => handleEdit(dessert)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={(e) => handleDelete(e, dessert.id, 'dessert')}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
        </>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && <UsersManagement />}

      {/* Logs Tab */}
      {activeTab === 'logs' && <ActivityLogsView />}
    </div>
  );
}

interface DessertFormProps {
  dessert: Dessert | null;
  onClose: () => void;
  onSave: () => void;
}

function DessertForm({ dessert, onClose, onSave }: DessertFormProps) {
  const [formData, setFormData] = useState<Partial<Dessert>>({
    title: dessert?.title || '',
    category: dessert?.category || '',
    image_url: dessert?.image_url || '',
    description: dessert?.description || '',
    ingredients: dessert?.ingredients || '',
    calories: dessert?.calories || null,
    proteins: dessert?.proteins || null,
    fats: dessert?.fats || null,
    carbs: dessert?.carbs || null,
    weight: dessert?.weight || '',
    price: dessert?.price || null,
    is_active: dessert?.is_active ?? true,
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const { error, success, warning } = useToastContext();

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const cats = await dessertsApi.getCategories();
      setCategories(cats);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (dessert) {
        await dessertsApi.update(dessert.id, formData);
      } else {
        await dessertsApi.create(formData as Omit<Dessert, 'id'>);
      }
      onSave();
      success(dessert ? 'Dessert updated successfully' : 'Dessert created successfully');
    } catch (err) {
      console.error('Error saving:', err);
      error('Error saving dessert');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          {dessert ? 'Edit Dessert' : 'Add Dessert'}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category * (можно указать несколько через запятую)
            </label>
            <input
              type="text"
              required
              list="categories-list"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="Начните вводить или выберите из списка..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <datalist id="categories-list">
              {categories.map((cat) => (
                <option key={cat} value={cat} />
              ))}
            </datalist>
            <p className="text-xs text-gray-500 mt-1">
              Пример: "Торты, Пирожные" или "Десерты"
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Image
            </label>
            
            {/* Превью изображения */}
            {formData.image_url && (
              <div className="mb-3">
                <img
                  src={getImageUrl(formData.image_url) || ''}
                  alt="Preview"
                  className="w-32 h-32 object-cover rounded-lg border border-gray-300"
                  onError={(e) => {
                    console.error('Error loading image:', formData.image_url);
                    e.currentTarget.style.display = 'none';
                  }}
                  onLoad={() => {
                    console.log('Image loaded:', formData.image_url);
                  }}
                />
                <div className="text-xs text-gray-500 mt-1">
                  URL: {formData.image_url}
                </div>
              </div>
            )}
            
            {/* File upload */}
            <div className="mb-2">
              <label className="block text-xs text-gray-600 mb-1">
                Upload File
              </label>
              <input
                type="file"
                accept="image/*"
                disabled={uploading}
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    // Проверка размера файла
                    if (file.size > 10 * 1024 * 1024) {
                      warning('File is too large. Maximum size: 10MB');
                      return;
                    }
                    
                    setUploading(true);
                    try {
                      console.log('Starting file upload:', file.name, file.size, 'type:', file.type);
                      
                      // Убеждаемся, что это действительно файл, а не путь
                      if (!(file instanceof File)) {
                        throw new Error('Selected object is not a file');
                      }
                      
                      const result = await uploadApi.uploadImage(file);
                      console.log('File uploaded, received result:', result);
                      
                      // Проверяем, что получили правильный URL
                      if (!result.url) {
                        throw new Error('Server did not return image URL');
                      }
                      
                      // Убеждаемся, что URL начинается с /static/images/ или http
                      if (!result.url.startsWith('/static/images/') && 
                          !result.url.startsWith('http://') && 
                          !result.url.startsWith('https://')) {
                        console.warn('Unexpected URL format:', result.url);
                      }
                      
                      console.log('Setting URL in form:', result.url);
                      setFormData({ ...formData, image_url: result.url });
                    } catch (err: any) {
                      console.error('Upload error:', err);
                      const errorMessage = err.response?.data?.detail || err.message || 'Error uploading image';
                      error(`Upload error: ${errorMessage}. Check browser console for details.`);
                    } finally {
                      setUploading(false);
                      // Clear input to allow uploading the same file again
                      e.target.value = '';
                    }
                  }
                }}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
              />
              {uploading && (
                <div className="mt-2 text-xs text-blue-600">Uploading image...</div>
              )}
            </div>
            
            {/* Or enter URL */}
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                Or enter URL (full URL or path /static/images/...)
              </label>
              <input
                type="text"
                value={formData.image_url || ''}
                onChange={(e) => {
                  let value = e.target.value;
                  // Remove local file system paths
                  if (value.startsWith('file://') || value.startsWith('C:\\') || value.startsWith('/Users/') || value.startsWith('/home/')) {
                    warning('Please use file upload or enter an image URL (http://... or /static/images/...)');
                    return;
                  }
                  setFormData({ ...formData, image_url: value });
                }}
                placeholder="https://example.com/image.jpg or /static/images/file.jpg"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ingredients
            </label>
            <textarea
              value={formData.ingredients || ''}
              onChange={(e) => setFormData({ ...formData, ingredients: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Calories (kcal)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.calories || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    calories: e.target.value ? parseFloat(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proteins (g)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.proteins || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    proteins: e.target.value ? parseFloat(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fats (g)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.fats || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    fats: e.target.value ? parseFloat(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Carbs (g)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.carbs || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    carbs: e.target.value ? parseFloat(e.target.value) : null,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Weight/Packaging
            </label>
            <input
              type="text"
              value={formData.weight || ''}
              onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price (THB)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.price || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  price: e.target.value ? parseFloat(e.target.value) : null,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="mr-2 w-4 h-4 text-blue-600"
              />
              <span className="text-sm text-gray-700">Active (show in catalog)</span>
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Компонент управления пользователями
function UsersManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const { error, success } = useToastContext();

  useEffect(() => {
    loadUsers();
  }, [search]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await usersApi.getAll({ search: search || undefined, limit: 100 });
      setUsers(data.users);
    } catch (err) {
      console.error('Error loading users:', err);
      error('Error loading users');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setShowEditForm(true);
  };

  const handleSave = async (userData: Partial<User>) => {
    if (!editingUser) return;
    
    try {
      await usersApi.update(editingUser.id, userData);
      await loadUsers();
      setShowEditForm(false);
      setEditingUser(null);
      success('User updated successfully');
    } catch (err) {
      console.error('Error updating user:', err);
      error('Error updating user');
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search users..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {showEditForm && editingUser && (
        <UserEditForm
          user={editingUser}
          onClose={() => {
            setShowEditForm(false);
            setEditingUser(null);
          }}
          onSave={handleSave}
        />
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Username
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{user.username}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{user.email}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-500">{user.company_name || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_admin
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {user.is_admin ? 'Admin' : 'User'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    type="button"
                    onClick={() => handleEdit(user)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && (
          <div className="text-center py-8 text-gray-500">No users found</div>
        )}
      </div>
    </div>
  );
}

interface UserEditFormProps {
  user: User;
  onClose: () => void;
  onSave: (data: Partial<User>) => void;
}

function UserEditForm({ user, onClose, onSave }: UserEditFormProps) {
  const [formData, setFormData] = useState({
    email: user.email,
    is_active: user.is_active,
    is_admin: user.is_admin,
    company_name: user.company_name || '',
    manager_contact: user.manager_contact || '',
    catalog_description: user.catalog_description || '',
  });
  const [saving, setSaving] = useState(false);
  const { error } = useToastContext();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await onSave(formData);
    } catch (err) {
      console.error('Error saving:', err);
      error('Error saving user');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Edit User: {user.username}</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Manager Contact</label>
            <textarea
              value={formData.manager_contact}
              onChange={(e) => setFormData({ ...formData, manager_contact: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Catalog Description</label>
            <textarea
              value={formData.catalog_description}
              onChange={(e) => setFormData({ ...formData, catalog_description: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="mr-2 w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-gray-700">Active</span>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_admin}
              onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
              className="mr-2 w-4 h-4 text-blue-600"
            />
            <span className="text-sm text-gray-700">Admin</span>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Компонент просмотра логов активности
function ActivityLogsView() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize] = useState(50);
  const [filters, setFilters] = useState({
    action: '',
    entity_type: '',
    username: '',
    search: '',
    days: 7,
  });
  const { error } = useToastContext();

  useEffect(() => {
    loadLogs();
  }, [page, filters]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params: any = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
      };
      if (filters.action) params.action = filters.action;
      if (filters.entity_type) params.entity_type = filters.entity_type;
      if (filters.username) params.username = filters.username;
      if (filters.search) params.search = filters.search;
      if (filters.days) params.days = filters.days;

      const data = await logsApi.getAll(params);
      setLogs(data.logs);
      setTotal(data.total);
    } catch (err) {
      console.error('Error loading logs:', err);
      error('Error loading logs');
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    if (action.includes('create')) return 'bg-green-100 text-green-800';
    if (action.includes('update')) return 'bg-blue-100 text-blue-800';
    if (action.includes('delete')) return 'bg-red-100 text-red-800';
    if (action.includes('login')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (loading && logs.length === 0) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Activity Logs</h2>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Action</label>
            <input
              type="text"
              placeholder="Filter by action..."
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Entity Type</label>
            <input
              type="text"
              placeholder="Filter by entity..."
              value={filters.entity_type}
              onChange={(e) => setFilters({ ...filters, entity_type: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Username</label>
            <input
              type="text"
              placeholder="Filter by user..."
              value={filters.username}
              onChange={(e) => setFilters({ ...filters, username: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search in logs..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Days</label>
            <select
              value={filters.days}
              onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {logs.length} of {total} logs
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{log.username || 'System'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getActionColor(log.action)}`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.entity_type ? `${log.entity_type}${log.entity_id ? ` #${log.entity_id}` : ''}` : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="max-w-md truncate" title={log.description || ''}>
                      {log.description || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.ip_address || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {logs.length === 0 && (
          <div className="text-center py-8 text-gray-500">No logs found</div>
        )}
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="mt-4 flex justify-between items-center">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {page} of {Math.ceil(total / pageSize)}
          </span>
          <button
            onClick={() => setPage(p => Math.min(Math.ceil(total / pageSize), p + 1))}
            disabled={page >= Math.ceil(total / pageSize)}
            className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

