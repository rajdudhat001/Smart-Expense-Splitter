import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { addMember, updateMember, getMembers } from '../services/api';
import { ArrowLeft, UserPlus, AlertCircle } from 'lucide-react';

export default function MemberForm() {
  const { groupId, memberId } = useParams();
  const navigate = useNavigate();
  const isEdit = !!memberId;

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isEdit) {
      const fetchMemberDetails = async () => {
        try {
          const res = await getMembers(groupId);
          const member = res.data.find(m => m.id === Number(memberId));
          if (member) {
            setName(member.name);
            setEmail(member.email || '');
            setPhone(member.phone || '');
          } else {
            setError('Member details not found.');
          }
        } catch (err) {
          setError('Failed to fetch member details.');
        }
      };
      fetchMemberDetails();
    }
  }, [groupId, memberId, isEdit]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setErrors({});
    setSubmitting(true);

    if (name.trim().length < 2) {
      setErrors({ name: ['Member name must be at least 2 characters long.'] });
      setSubmitting(false);
      return;
    }

    const payload = { name: name.trim(), email: email.trim(), phone: phone.trim() };

    try {
      if (isEdit) {
        await updateMember(groupId, memberId, payload);
      } else {
        await addMember(groupId, payload);
      }
      navigate(`/groups/${groupId}`);
    } catch (err) {
      if (err.response && err.response.data) {
        if (err.response.data.name) {
          setErrors({ name: err.response.data.name });
        } else if (err.response.data.non_field_errors || err.response.data.detail) {
          setError(err.response.data.non_field_errors?.[0] || err.response.data.detail || err.response.data.name?.[0]);
        } else {
          setErrors(err.response.data);
        }
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto animate-fade-in">
      <Link to={`/groups/${groupId}`} className="text-indigo-400 hover:text-indigo-300 font-semibold mb-6 inline-flex items-center space-x-1 text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Group</span>
      </Link>

      <div className="glass-panel rounded-2xl p-8">
        <div className="flex items-center space-x-3 mb-6">
          <UserPlus className="w-6 h-6 text-indigo-400" />
          <h2 className="text-2xl font-bold text-white font-sans">
            {isEdit ? 'Edit Group Member' : 'Add Group Member'}
          </h2>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="memberName" className="block text-slate-300 text-sm font-medium mb-1.5">
              Member Name
            </label>
            <input
              id="memberName"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={`w-full px-4 py-2.5 rounded-xl glass-input text-sm font-sans ${errors.name ? 'border-rose-500/50 focus:border-rose-500' : ''}`}
              placeholder="e.g. John Doe"
            />
            {errors.name && (
              <p className="mt-1 text-xs text-rose-400">{errors.name[0]}</p>
            )}
          </div>

          <div>
            <label htmlFor="memberEmail" className="block text-slate-300 text-sm font-medium mb-1.5">
              Email Address (Optional)
            </label>
            <input
              id="memberEmail"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`w-full px-4 py-2.5 rounded-xl glass-input text-sm font-sans ${errors.email ? 'border-rose-500/50 focus:border-rose-500' : ''}`}
              placeholder="john@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-xs text-rose-400">{errors.email[0]}</p>
            )}
          </div>

          <div>
            <label htmlFor="memberPhone" className="block text-slate-300 text-sm font-medium mb-1.5">
              Phone Number (Optional)
            </label>
            <input
              id="memberPhone"
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className={`w-full px-4 py-2.5 rounded-xl glass-input text-sm font-sans ${errors.phone ? 'border-rose-500/50 focus:border-rose-500' : ''}`}
              placeholder="e.g. +91 98765 43210"
            />
            {errors.phone && (
              <p className="mt-1 text-xs text-rose-400">{errors.phone[0]}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700/50 text-white rounded-xl text-sm font-semibold transition-all flex items-center justify-center space-x-2"
          >
            {submitting ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <span>{isEdit ? 'Save Changes' : 'Add Member'}</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
