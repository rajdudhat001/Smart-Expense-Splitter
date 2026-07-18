import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  getGroupDetail, deleteGroup, getMembers, deleteMember,
  getExpenses, deleteExpense, getGroupBudget, setGroupBudget, inviteMember
} from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { 
  Users, DollarSign, Settings, Trash2, Edit3, Plus, 
  ChevronRight, Calendar, AlertTriangle, ArrowLeft,
  ChevronDown, ChevronUp, Bell, DollarSign as MoneyIcon
} from 'lucide-react';

export default function GroupDetails() {
  const { groupId } = useParams();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  // Group Details state
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Sub-data states
  const [members, setMembers] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [totalSpent, setTotalSpent] = useState(0);
  const [expandedExpenseId, setExpandedExpenseId] = useState(null);

  // Budget states
  const [budget, setBudget] = useState(null);
  const [isBudgetExceeded, setIsBudgetExceeded] = useState(false);
  const [newBudgetLimit, setNewBudgetLimit] = useState('');
  const [settingBudget, setSettingBudget] = useState(false);

  // Active view states
  const [isCreator, setIsCreator] = useState(false);

  // Invitation states
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviting, setInviting] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState('');
  const [inviteError, setInviteError] = useState('');

  const handleInviteUser = async (e) => {
    e.preventDefault();
    setInviteError('');
    setInviteSuccess('');
    if (!inviteEmail.trim()) return;
    setInviting(true);
    try {
      await inviteMember(groupId, { email: inviteEmail.trim() });
      setInviteSuccess('Invitation sent successfully!');
      setInviteEmail('');
    } catch (err) {
      setInviteError(err.response?.data?.email?.[0] || err.response?.data?.detail || 'Failed to send invitation.');
    } finally {
      setInviting(false);
    }
  };

  const loadAllData = async () => {
    try {
      const groupRes = await getGroupDetail(groupId);
      setGroup(groupRes.data);
      setIsCreator(groupRes.data.created_by.id === user?.id);

      const membersRes = await getMembers(groupId);
      setMembers(membersRes.data);

      const expensesRes = await getExpenses(groupId);
      setExpenses(expensesRes.data.expenses);
      setTotalSpent(Number(expensesRes.data.total_amount));

      const budgetRes = await getGroupBudget(groupId);
      setBudget(budgetRes.data.budget);
      setIsBudgetExceeded(budgetRes.data.is_exceeded);
      if (budgetRes.data.budget) {
        setNewBudgetLimit(budgetRes.data.budget.amount_limit);
      }
    } catch (err) {
      setError('Failed to fetch group details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [groupId]);

  const handleDeleteGroup = async () => {
    if (!window.confirm('Are you sure you want to delete this group? This action is permanent.')) return;
    try {
      await deleteGroup(groupId);
      navigate('/');
    } catch (err) {
      setError('Failed to delete group.');
    }
  };

  const handleDeleteMember = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove member ${name}?`)) return;
    try {
      await deleteMember(groupId, id);
      loadAllData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete member.');
    }
  };

  const handleDeleteExpense = async (id, title) => {
    if (!window.confirm(`Are you sure you want to delete expense "${title}"?`)) return;
    try {
      await deleteExpense(groupId, id);
      loadAllData();
    } catch (err) {
      setError('Failed to delete expense.');
    }
  };

  const handleSetBudget = async (e) => {
    e.preventDefault();
    if (!newBudgetLimit || Number(newBudgetLimit) <= 0) return;
    setSettingBudget(true);
    try {
      await setGroupBudget(groupId, { amount_limit: newBudgetLimit });
      loadAllData();
    } catch (err) {
      setError('Failed to update budget limit.');
    } finally {
      setSettingBudget(false);
    }
  };

  const toggleExpenseExpansion = async (expenseId) => {
    if (expandedExpenseId === expenseId) {
      setExpandedExpenseId(null);
    } else {
      setExpandedExpenseId(expenseId);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-white">Group Not Found</h2>
        <Link to="/" className="text-indigo-400 hover:text-indigo-300 font-medium mt-4 inline-flex items-center space-x-1">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </Link>
      </div>
    );
  }

  const budgetProgress = budget ? Math.min((totalSpent / Number(budget.amount_limit)) * 100, 100) : 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Navigation & Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <Link to="/" className="text-indigo-400 hover:text-indigo-300 font-semibold mb-2 inline-flex items-center space-x-1 text-sm transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>
          <div className="flex items-center space-x-3 mt-1">
            <h1 className="text-3xl font-extrabold text-white tracking-tight font-sans">
              {group.name}
            </h1>
            {isCreator ? (
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Owner
              </span>
            ) : (
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-400 border border-slate-700/30">
                Member
              </span>
            )}
          </div>
          <p className="text-slate-400 text-sm mt-1">{group.description || 'No description provided.'}</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            to={`/groups/${groupId}/balances`}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/20"
          >
            Balances & Settlements
          </Link>

          {isCreator && (
            <button
              onClick={handleDeleteGroup}
              className="p-2.5 rounded-xl border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-colors"
              title="Delete Group"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-2.5">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Budget Limit Exceeded Alert Banner */}
      {budget && isBudgetExceeded && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm flex items-center justify-between animate-pulse-slow">
          <div className="flex items-center space-x-2.5">
            <AlertTriangle className="w-5 h-5" />
            <span>
              <strong>Budget Warning:</strong> Total expenses (₹{totalSpent.toFixed(2)}) exceed group budget (₹{Number(budget.amount_limit).toFixed(2)}).
            </span>
          </div>
        </div>
      )}

      {/* Primary Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Members & Budget */}
        <div className="space-y-8 lg:col-span-1">
          {/* Members Panel */}
          <div className="glass-panel rounded-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center space-x-2.5">
                <Users className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white font-sans">Members</h3>
              </div>
              {isCreator && (
                <Link
                  to={`/groups/${groupId}/members/add`}
                  className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 hover:bg-indigo-500/20 transition-all"
                  title="Add Member"
                >
                  <Plus className="w-4 h-4" />
                </Link>
              )}
            </div>

            {members.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-6">No members added yet.</p>
            ) : (
              <div className="divide-y divide-slate-800/40">
                {members.map((member) => (
                  <div key={member.id} className="py-3 flex justify-between items-center group">
                    <div>
                      <Link
                        to={`/groups/${groupId}/members/${member.id}/ledger`}
                        className="font-medium text-slate-200 hover:text-indigo-400 transition-colors text-sm"
                      >
                        {member.name}
                      </Link>
                      <p className="text-[11px] text-slate-500">{member.email || 'No email'}</p>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <Link
                        to={`/groups/${groupId}/members/${member.id}/ledger`}
                        className="text-[11px] font-semibold text-indigo-400 hover:underline px-2 py-1 rounded"
                      >
                        Ledger
                      </Link>

                      {isCreator && (
                        <>
                          <Link
                            to={`/groups/${groupId}/members/${member.id}/edit`}
                            className="p-1 text-slate-500 hover:text-slate-300 transition-colors opacity-0 group-hover:opacity-100"
                            title="Edit Member"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </Link>
                          <button
                            onClick={() => handleDeleteMember(member.id, member.name)}
                            className="p-1 text-rose-500/70 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100"
                            title="Remove Member"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {isCreator && (
              <form onSubmit={handleInviteUser} className="mt-4 pt-4 border-t border-slate-800/40 space-y-2">
                <label htmlFor="inviteEmail" className="block text-slate-400 text-[10px] font-semibold uppercase tracking-wider">
                  Invite Member by Email
                </label>
                {inviteSuccess && <p className="text-emerald-400 text-xs">{inviteSuccess}</p>}
                {inviteError && <p className="text-rose-400 text-xs">{inviteError}</p>}
                <div className="flex items-center space-x-2">
                  <input
                    id="inviteEmail"
                    type="email"
                    required
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-lg glass-input text-xs"
                    placeholder="friend@example.com"
                  />
                  <button
                    type="submit"
                    disabled={inviting}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700/50 text-white rounded-lg text-xs font-semibold cursor-pointer"
                  >
                    {inviting ? '...' : 'Invite'}
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Budget Limit Configurations */}
          <div className="glass-panel rounded-2xl p-6">
            <div className="flex items-center space-x-2.5 mb-4">
              <Bell className="w-5 h-5 text-indigo-400" />
              <h3 className="text-lg font-bold text-white font-sans">Group Budget</h3>
            </div>

            {budget ? (
              <div className="space-y-4">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Spend Progress</span>
                  <span>{budgetProgress.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${isBudgetExceeded ? 'bg-rose-500' : 'bg-indigo-500'}`}
                    style={{ width: `${budgetProgress}%` }}
                  ></div>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Total Spent: <span className="text-white font-semibold">₹{totalSpent.toFixed(2)}</span> of <span className="text-indigo-400 font-semibold">₹{Number(budget.amount_limit).toFixed(2)}</span>
                </p>
              </div>
            ) : (
              <p className="text-slate-500 text-xs py-2">No budget limit set for this group.</p>
            )}

            {isCreator && (
              <form onSubmit={handleSetBudget} className="mt-4 pt-4 border-t border-slate-800/40 flex items-end space-x-2">
                <div className="flex-1">
                  <label htmlFor="budgetLimit" className="block text-slate-400 text-[10px] font-semibold uppercase tracking-wider mb-1">
                    {budget ? 'Update' : 'Set'} Limit (₹)
                  </label>
                  <input
                    id="budgetLimit"
                    type="number"
                    required
                    min="1"
                    step="0.01"
                    value={newBudgetLimit}
                    onChange={(e) => setNewBudgetLimit(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg glass-input text-xs"
                    placeholder="Enter budget limit"
                  />
                </div>
                <button
                  type="submit"
                  disabled={settingBudget}
                  className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700/50 text-white rounded-lg text-xs font-semibold transition-colors flex-shrink-0"
                >
                  {settingBudget ? '...' : 'Save'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Right Column: Expense History & Split Details */}
        <div className="space-y-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold text-white font-sans">Expenses History</h2>
            {isCreator && (
              <Link
                to={`/groups/${groupId}/expenses/add`}
                className="flex items-center space-x-1.5 px-3 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/20 text-indigo-400 hover:text-indigo-300 font-semibold text-xs rounded-xl transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Add Expense</span>
              </Link>
            )}
          </div>

          {expenses.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 text-center">
              <MoneyIcon className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-300">No Expenses Recorded</h3>
              <p className="text-slate-500 text-sm mt-1 max-w-sm mx-auto">
                No bills have been posted in this group. Click 'Add Expense' above to create one.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {expenses.map((expense) => {
                const isExpanded = expandedExpenseId === expense.id;
                return (
                  <div key={expense.id} className="glass-panel rounded-2xl overflow-hidden transition-all duration-300">
                    <div 
                      onClick={() => toggleExpenseExpansion(expense.id)}
                      className="p-5 flex justify-between items-center cursor-pointer hover:bg-slate-800/10 transition-colors"
                    >
                      <div className="space-y-1 pr-4">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-bold text-slate-200 text-base font-sans line-clamp-1">{expense.title}</h4>
                          <span className="text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/30">
                            {expense.category}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-slate-500 text-[11px]">
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3.5 h-3.5" />
                            <span>{new Date(expense.date).toLocaleDateString()}</span>
                          </span>
                          <span>•</span>
                          <span>Paid by: <strong className="text-slate-300">{expense.paid_by_name}</strong></span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-4">
                        <span className="font-bold text-white text-lg font-sans">
                          ₹{Number(expense.amount).toFixed(2)}
                        </span>
                        {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-5 pb-5 pt-3 border-t border-slate-800/40 bg-slate-950/20 space-y-4 animate-slide-down">
                        {expense.description && (
                          <div className="text-slate-400 text-xs">
                            <h5 className="font-semibold text-slate-300 uppercase tracking-wider text-[9px] mb-1">Description</h5>
                            <p>{expense.description}</p>
                          </div>
                        )}

                        {expense.notes && (
                          <div className="text-slate-400 text-xs">
                            <h5 className="font-semibold text-slate-300 uppercase tracking-wider text-[9px] mb-1">Notes</h5>
                            <p>{expense.notes}</p>
                          </div>
                        )}

                        {/* Splitting Details */}
                        <div className="pt-2">
                          <div className="flex justify-between items-center mb-2">
                            <h5 className="font-semibold text-slate-300 uppercase tracking-wider text-[9px]">Splits Shares</h5>
                            {isCreator && (
                              <Link
                                to={`/groups/${groupId}/expenses/${expense.id}/split`}
                                className="text-[10px] font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                              >
                                {expense.splits && expense.splits.length > 0 ? 'Edit Split' : 'Setup Split'}
                              </Link>
                            )}
                          </div>

                          {!expense.splits || expense.splits.length === 0 ? (
                            <div className="text-center py-4 bg-slate-900/30 rounded-xl border border-dashed border-slate-800/50">
                              <p className="text-slate-500 text-xs">This expense hasn't been split yet.</p>
                              {isCreator && (
                                <Link
                                  to={`/groups/${groupId}/expenses/${expense.id}/split`}
                                  className="mt-2 inline-block px-3 py-1.5 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 rounded-lg text-xs font-semibold"
                                >
                                  Setup Splits Now
                                </Link>
                              )}
                            </div>
                          ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 bg-slate-900/30 border border-slate-800/40 rounded-xl p-3.5">
                              {expense.splits.map((split) => (
                                <div key={split.id} className="flex justify-between items-center text-xs py-1 border-b border-slate-800/20 last:border-0">
                                  <span className="text-slate-300">{split.member_name}</span>
                                  <span className="font-semibold text-slate-200">₹{Number(split.amount).toFixed(2)}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Creator options */}
                        {isCreator && (
                          <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800/40 text-xs">
                            <Link
                              to={`/groups/${groupId}/expenses/${expense.id}/edit`}
                              className="flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-500 text-slate-300 hover:bg-slate-800/30 transition-all"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                              <span>Edit</span>
                            </Link>
                            <button
                              onClick={() => handleDeleteExpense(expense.id, expense.title)}
                              className="flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-all"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                              <span>Delete</span>
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
