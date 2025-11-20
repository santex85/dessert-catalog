import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, uploadApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useToastContext } from '../contexts/ToastContext';
import { getImageUrl } from '../utils/image';

export default function Profile() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const { success, error } = useToastContext();
  
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [uploadingLogo, setUploadingLogo] = useState(false);
  
  const [logoUrl, setLogoUrl] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [managerContact, setManagerContact] = useState('');

  useEffect(() => {
    if (user) {
      setEmail(user.email || '');
      setLogoUrl(user.logo_url || '');
      setCompanyName(user.company_name || '');
      setManagerContact(user.manager_contact || '');
    }
  }, [user]);

  const handleUpdateEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      error('Please enter a valid email address');
      return;
    }

    if (email === user?.email) {
      error('New email must be different from current email');
      return;
    }

    try {
      setEmailLoading(true);
      const response = await authApi.updateEmail(email);
      success('Email updated successfully');
      await refreshUser();
      setEmail(response.user.email);
    } catch (err: any) {
      console.error('Error updating email:', err);
      error(err.response?.data?.detail || 'Error updating email');
    } finally {
      setEmailLoading(false);
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!currentPassword || !newPassword || !confirmPassword) {
      error('Please fill in all password fields');
      return;
    }

    if (newPassword.length < 6) {
      error('Password must be at least 6 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      error('New passwords do not match');
      return;
    }

    if (currentPassword === newPassword) {
      error('New password must be different from current password');
      return;
    }

    try {
      setPasswordLoading(true);
      await authApi.updatePassword(currentPassword, newPassword);
      success('Password updated successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      console.error('Error updating password:', err);
      error(err.response?.data?.detail || 'Error updating password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleUpdateCompanyProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setCompanyLoading(true);
      await authApi.updateCompanyProfile({
        logo_url: logoUrl || undefined,
        company_name: companyName || undefined,
        manager_contact: managerContact || undefined,
      });
      success('Company profile updated successfully');
      await refreshUser();
    } catch (err: any) {
      console.error('Error updating company profile:', err);
      error(err.response?.data?.detail || 'Error updating company profile');
    } finally {
      setCompanyLoading(false);
    }
  };

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      error('File is too large. Maximum size: 10MB');
      return;
    }

    try {
      setUploadingLogo(true);
      const result = await uploadApi.uploadImage(file);
      setLogoUrl(result.url);
      // Автоматически сохраняем после загрузки
      await authApi.updateCompanyProfile({
        logo_url: result.url,
        company_name: companyName || undefined,
        manager_contact: managerContact || undefined,
      });
      await refreshUser();
      success('Logo uploaded successfully');
    } catch (err: any) {
      console.error('Error uploading logo:', err);
      error(err.response?.data?.detail || 'Error uploading logo');
    } finally {
      setUploadingLogo(false);
      e.target.value = '';
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Back to Catalog
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Information</h2>
          <div className="space-y-2">
            <div>
              <span className="text-sm font-medium text-gray-500">Username:</span>
              <span className="ml-2 text-gray-900">{user.username}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Email:</span>
              <span className="ml-2 text-gray-900">{user.email}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Role:</span>
              <span className="ml-2 text-gray-900">{user.is_admin ? 'Administrator' : 'User'}</span>
            </div>
            {user.created_at && (
              <div>
                <span className="text-sm font-medium text-gray-500">Member since:</span>
                <span className="ml-2 text-gray-900">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Update Email</h2>
          <form onSubmit={handleUpdateEmail} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                New Email
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter new email"
                required
              />
            </div>
            <button
              type="submit"
              disabled={emailLoading || email === user.email}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {emailLoading ? 'Updating...' : 'Update Email'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Change Password</h2>
          <form onSubmit={handleUpdatePassword} className="space-y-4">
            <div>
              <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Current Password
              </label>
              <input
                type="password"
                id="currentPassword"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter current password"
                required
              />
            </div>
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter new password (minimum 6 characters)"
                required
                minLength={6}
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Confirm new password"
                required
                minLength={6}
              />
            </div>
            <button
              type="submit"
              disabled={passwordLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {passwordLoading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Company Profile</h2>
          <p className="text-sm text-gray-600 mb-4">
            This information will be used on the title page of PDF catalogs
          </p>
          <form onSubmit={handleUpdateCompanyProfile} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Logo
              </label>
              {logoUrl && (
                <div className="mb-3">
                  <img
                    src={getImageUrl(logoUrl) || logoUrl}
                    alt="Company logo"
                    className="w-32 h-32 object-contain border border-gray-300 rounded-lg p-2"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                disabled={uploadingLogo}
                onChange={handleLogoUpload}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
              />
              {uploadingLogo && (
                <div className="mt-2 text-xs text-blue-600">Uploading logo...</div>
              )}
              {logoUrl && (
                <button
                  type="button"
                  onClick={() => {
                    setLogoUrl('');
                    authApi.updateCompanyProfile({
                      logo_url: '',
                      company_name: companyName || undefined,
                      manager_contact: managerContact || undefined,
                    }).then(() => {
                      refreshUser();
                      success('Logo removed');
                    });
                  }}
                  className="mt-2 text-sm text-red-600 hover:text-red-800"
                >
                  Remove logo
                </button>
              )}
            </div>

            <div>
              <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-1">
                Company Name
              </label>
              <input
                type="text"
                id="companyName"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter company name"
              />
            </div>

            <div>
              <label htmlFor="managerContact" className="block text-sm font-medium text-gray-700 mb-1">
                Manager Contact
              </label>
              <input
                type="text"
                id="managerContact"
                value={managerContact}
                onChange={(e) => setManagerContact(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Phone, email, etc."
              />
            </div>

            <button
              type="submit"
              disabled={companyLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {companyLoading ? 'Saving...' : 'Save Company Profile'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

