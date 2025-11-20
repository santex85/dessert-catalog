import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import DessertCard from './DessertCard';
import DessertModal from './DessertModal';
import PDFExportModal from './PDFExportModal';
import { Dessert } from '../types';
import { dessertsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface CatalogProps {
  desserts: Dessert[];
}

export default function Catalog({ desserts: initialDesserts }: CatalogProps) {
  const [desserts, setDesserts] = useState<Dessert[]>(initialDesserts);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDessert, setSelectedDessert] = useState<Dessert | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [showPDFModal, setShowPDFModal] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

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

  const filteredDesserts = useMemo(() => {
    return desserts.filter((dessert) => {
      // Поддержка нескольких категорий через запятую
      let matchesCategory = true;
      if (selectedCategory) {
        const dessertCategories = dessert.category.split(',').map(c => c.trim().toLowerCase());
        matchesCategory = dessertCategories.includes(selectedCategory.toLowerCase());
      }
      
      const matchesSearch = !searchQuery || 
        dessert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (dessert.description && dessert.description.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesCategory && matchesSearch;
    });
  }, [desserts, selectedCategory, searchQuery]);

  const toggleSelection = (id: number) => {
    const newSelection = new Set(selectedIds);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedIds(newSelection);
  };

  const selectAll = () => {
    if (selectedIds.size === filteredDesserts.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredDesserts.map(d => d.id)));
    }
  };

  return (
    <>
      <div className="mb-6 space-y-4">
        {/* Поиск и фильтры */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Кнопки управления выбором */}
        <div className="flex justify-between items-center">
          <button
            onClick={selectAll}
            className="px-4 py-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            {selectedIds.size === filteredDesserts.length ? 'Deselect All' : 'Select All'}
          </button>
          {selectedIds.size > 0 && (
            <span className="text-sm text-gray-600">
              Selected: {selectedIds.size}
            </span>
          )}
        </div>
      </div>

      {/* Сетка карточек */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredDesserts.map((dessert) => (
          <DessertCard
            key={dessert.id}
            dessert={dessert}
            isSelected={selectedIds.has(dessert.id)}
            onSelect={() => toggleSelection(dessert.id)}
            onClick={() => setSelectedDessert(dessert)}
          />
        ))}
      </div>

      {filteredDesserts.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No desserts found
        </div>
      )}

      {/* Плавающая кнопка скачивания PDF */}
      {selectedIds.size > 0 && (
        <button
          onClick={() => {
            if (!isAuthenticated) {
              navigate('/login');
            } else {
              setShowPDFModal(true);
            }
          }}
          className="fixed bottom-8 right-8 bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg hover:bg-blue-700 transition-all transform hover:scale-105 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download Catalog ({selectedIds.size})
        </button>
      )}

      {/* Модальное окно с деталями десерта */}
      {selectedDessert && (
        <DessertModal
          dessert={selectedDessert}
          onClose={() => setSelectedDessert(null)}
        />
      )}

      {/* Модальное окно экспорта PDF */}
      {showPDFModal && (
        <PDFExportModal
          selectedIds={Array.from(selectedIds)}
          onClose={() => setShowPDFModal(false)}
        />
      )}
    </>
  );
}

