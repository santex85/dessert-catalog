import { useState, useEffect } from 'react';
import { Dessert } from '../types';
import { dessertsApi, uploadApi } from '../services/api';
import { getImageUrl } from '../utils/image';
import { useToastContext } from '../contexts/ToastContext';
import ConfirmDialog from './ConfirmDialog';

interface AdminPanelProps {
  onUpdate: () => void;
}

export default function AdminPanel({ onUpdate }: AdminPanelProps) {
  const [desserts, setDesserts] = useState<Dessert[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingDessert, setEditingDessert] = useState<Dessert | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number } | null>(null);
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

  const handleDelete = (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    setDeleteConfirm({ id });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    
    try {
      await dessertsApi.delete(deleteConfirm.id);
      await loadDesserts();
      onUpdate();
      success('Dessert deleted successfully');
    } catch (err) {
      console.error('Error deleting:', err);
      error('Error deleting dessert');
    } finally {
      setDeleteConfirm(null);
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

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  return (
    <div>
      {deleteConfirm && (
        <ConfirmDialog
          title="Delete Dessert"
          message="Are you sure you want to delete this dessert? This action cannot be undone."
          confirmText="Delete"
          cancelText="Cancel"
          type="danger"
          onConfirm={confirmDelete}
          onCancel={() => setDeleteConfirm(null)}
        />
      )}

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
        <table className="min-w-full divide-y divide-gray-200">
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
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{dessert.category}</div>
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
                    onClick={(e) => handleDelete(e, dessert.id)}
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
    is_active: dessert?.is_active ?? true,
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const { error, success, warning } = useToastContext();

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
              Category *
            </label>
            <input
              type="text"
              required
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
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

