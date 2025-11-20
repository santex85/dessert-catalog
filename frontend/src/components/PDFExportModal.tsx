import { useState, useEffect } from 'react';
import { pdfApi } from '../services/api';
import { PDFExportSettings, PDFTemplate } from '../types';
import { useToastContext } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';

interface PDFExportModalProps {
  selectedIds: number[];
  onClose: () => void;
}

const templates: PDFTemplate[] = [
  {
    id: 'minimal',
    name: 'Minimalist',
    description: 'Clean and simple design, focus on content'
  },
  {
    id: 'classic',
    name: 'Classic',
    description: 'Elegant style with decorative elements'
  },
  {
    id: 'modern',
    name: 'Modern',
    description: 'Bright design with colorful accents'
  },
  {
    id: 'luxury',
    name: 'Luxury',
    description: 'Luxurious style with gold accents'
  },
];

export default function PDFExportModal({ selectedIds, onClose }: PDFExportModalProps) {
  const { user } = useAuth();
  const [settings, setSettings] = useState<PDFExportSettings>({
    dessert_ids: selectedIds,
    include_ingredients: true,
    include_nutrition: true,
    include_title_page: true,
    company_name: '',
    manager_contact: '',
    template: 'minimal',
  });
  const [loading, setLoading] = useState(false);
  const { error, success } = useToastContext();

  useEffect(() => {
    // Заполняем данные из профиля пользователя
    if (user) {
      setSettings(prev => ({
        ...prev,
        company_name: user.company_name || '',
        manager_contact: user.manager_contact || '',
        logo_url: user.logo_url || '',
      }));
    }
  }, [user]);

  const handleExport = async () => {
    try {
      setLoading(true);
      const blob = await pdfApi.export(settings);
      
      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'catalog.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      success('PDF generated and downloaded successfully');
      onClose();
    } catch (err) {
      console.error('PDF generation error:', err);
      error('Error generating PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
        <div
          className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
          onClick={(e) => e.stopPropagation()}
        >
        <h2 className="text-2xl font-bold text-gray-900 mb-6">PDF Export Settings</h2>

        <div className="space-y-6">
          {/* Выбор шаблона */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Design Template
            </label>
            <div className="grid grid-cols-2 gap-3">
              {templates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => setSettings({ ...settings, template: template.id })}
                  className={`p-4 border-2 rounded-lg text-left transition-all ${
                    settings.template === template.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-semibold text-gray-900 mb-1">{template.name}</div>
                  <div className="text-xs text-gray-600">{template.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Опции экспорта */}
          <div className="space-y-3 pt-3 border-t">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.include_ingredients}
                onChange={(e) =>
                  setSettings({ ...settings, include_ingredients: e.target.checked })
                }
                className="mr-3 w-4 h-4 text-blue-600"
              />
              <span className="text-gray-700">Include Ingredients</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.include_nutrition}
                onChange={(e) =>
                  setSettings({ ...settings, include_nutrition: e.target.checked })
                }
                className="mr-3 w-4 h-4 text-blue-600"
              />
              <span className="text-gray-700">Include Nutrition</span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.include_title_page}
                onChange={(e) =>
                  setSettings({ ...settings, include_title_page: e.target.checked })
                }
                className="mr-3 w-4 h-4 text-blue-600"
              />
              <span className="text-gray-700">Add Title Page</span>
            </label>
          </div>

          {/* Дополнительные поля для титульного листа */}
          {settings.include_title_page && (
            <div className="space-y-3 pt-3 border-t">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  value={settings.company_name || ''}
                  onChange={(e) =>
                    setSettings({ ...settings, company_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="ООО Кондитерская"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Manager Contact
                </label>
                <input
                  type="text"
                  value={settings.manager_contact || ''}
                  onChange={(e) =>
                    setSettings({ ...settings, manager_contact: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+7 (999) 123-45-67, manager@example.com"
                />
              </div>
            </div>
          )}

          <div className="text-sm text-gray-500 pt-2">
            Desserts to export: {selectedIds.length}
          </div>
        </div>

        {/* Кнопки */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Download PDF'}
          </button>
        </div>
      </div>
    </div>
  );
}

