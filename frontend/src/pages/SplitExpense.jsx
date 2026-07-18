import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getExpenseDetail, getMembers, previewEqualSplit, saveExpenseSplits } from '../services/api';
import { ArrowLeft, CheckSquare, Square, AlertCircle, RefreshCw } from 'lucide-react';

export default function SplitExpense() {
  const { groupId, expenseId } = useParams();
  const navigate = useNavigate();

  // Data states
  const [expense, setExpense] = useState(null);
  const [members, setMembers] = useState([]);
  const [selectedMemberIds, setSelectedMemberIds] = useState([]);
  
  // View states
  const [splitMethod, setSplitMethod] = useState('equal'); // 'equal' or 'unequal'
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Equal Split Preview State
  const [equalPreview, setEqualPreview] = useState([]);

  // Unequal Split Custom Inputs State (member_id -> amount string)
  const [unequalAmounts, setUnequalAmounts] = useState({});

  useEffect(() => {
    const loadSplitInfo = async () => {
      try {
        const expRes = await getExpenseDetail(groupId, expenseId);
        setExpense(expRes.data);

        const membersRes = await getMembers(groupId);
        setMembers(membersRes.data);

        // Pre-select all members by default
        const allIds = membersRes.data.map(m => m.id);
        setSelectedMemberIds(allIds);

        // Check if there are already splits saved for this expense
        if (expRes.data.splits && expRes.data.splits.length > 0) {
          // Pre-populate based on existing splits
          const activeSplits = expRes.data.splits.filter(s => Number(s.amount) > 0);
          const activeIds = activeSplits.map(s => s.member);
          setSelectedMemberIds(activeIds);
          
          // Determine split method if saved splits are unequal
          const firstVal = Number(activeSplits[0]?.amount);
          const isAllEqual = activeSplits.every(s => Math.abs(Number(s.amount) - firstVal) < 0.01);
          
          if (!isAllEqual) {
            setSplitMethod('unequal');
            const amountsMap = {};
            expRes.data.splits.forEach(s => {
              if (Number(s.amount) > 0) {
                amountsMap[s.member] = Number(s.amount).toFixed(2);
              }
            });
            setUnequalAmounts(amountsMap);
          }
        }
      } catch (err) {
        setError('Failed to load expense split page.');
      } finally {
        setLoading(false);
      }
    };
    loadSplitInfo();
  }, [groupId, expenseId]);

  // Handle member checkbox toggle
  const toggleMemberSelection = (id) => {
    if (selectedMemberIds.includes(id)) {
      setSelectedMemberIds(selectedMemberIds.filter(mid => mid !== id));
    } else {
      setSelectedMemberIds([...selectedMemberIds, id]);
    }
    // Reset calculations
    setEqualPreview([]);
  };

  // Select all / Deselect all
  const selectAll = () => {
    setSelectedMemberIds(members.map(m => m.id));
    setEqualPreview([]);
  };

  const selectNone = () => {
    setSelectedMemberIds([]);
    setEqualPreview([]);
  };

  // Run dynamic calculation on equal split
  const handleCalculateEqual = async () => {
    if (selectedMemberIds.length === 0) {
      setError('Please select at least one member to split with.');
      return;
    }
    setError('');
    setCalculating(true);
    try {
      const response = await previewEqualSplit(groupId, expenseId, { member_ids: selectedMemberIds });
      setEqualPreview(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error calculating equal split.');
    } finally {
      setCalculating(false);
    }
  };

  // Trigger calculation when changing method or selections
  useEffect(() => {
    if (splitMethod === 'equal' && selectedMemberIds.length > 0 && expense) {
      handleCalculateEqual();
    }
  }, [splitMethod, selectedMemberIds, expense]);

  // Sum total of custom entered shares for Unequal split
  const getUnequalTotal = () => {
    let total = 0;
    selectedMemberIds.forEach(mid => {
      const val = Number(unequalAmounts[mid] || 0);
      if (!isNaN(val)) total += val;
    });
    return total;
  };

  const handleSaveSplits = async () => {
    setError('');
    setSaving(true);

    if (selectedMemberIds.length === 0) {
      setError('Please select at least one member.');
      setSaving(false);
      return;
    }

    let finalSplits = [];
    const totalExpenseAmount = Number(expense.amount);

    if (splitMethod === 'equal') {
      if (equalPreview.length === 0) {
        setError('Please calculate the splits first.');
        setSaving(false);
        return;
      }
      finalSplits = equalPreview.map(p => ({
        member_id: p.member_id,
        amount: Number(p.amount)
      }));
    } else {
      // Unequal split validation
      let sum = 0;
      let hasNegative = false;
      
      for (let mid of selectedMemberIds) {
        const valStr = unequalAmounts[mid] || '0.00';
        const val = Number(valStr);
        if (isNaN(val) || val < 0) {
          hasNegative = true;
          break;
        }
        sum += val;
        finalSplits.push({
          member_id: mid,
          amount: val
        });
      }

      if (hasNegative) {
        setError('Split amounts must be valid non-negative numbers.');
        setSaving(false);
        return;
      }

      const diff = Math.abs(totalExpenseAmount - sum);
      if (diff >= 0.01) {
        setError(`Total entered splits (₹${sum.toFixed(2)}) must exactly match the expense amount (₹${totalExpenseAmount.toFixed(2)}). Difference is ₹${(totalExpenseAmount - sum).toFixed(2)}.`);
        setSaving(false);
        return;
      }
    }

    try {
      await saveExpenseSplits(groupId, expenseId, {
        split_method: splitMethod,
        splits: finalSplits
      });
      navigate(`/groups/${groupId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save expense splits.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const unequalTotal = getUnequalTotal();
  const expenseAmount = Number(expense.amount);
  const unequalDiff = expenseAmount - unequalTotal;

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <Link to={`/groups/${groupId}`} className="text-indigo-400 hover:text-indigo-300 font-semibold mb-6 inline-flex items-center space-x-1 text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Group</span>
      </Link>

      <div className="glass-panel rounded-2xl p-8 space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-white font-sans">Split Expense</h2>
          <p className="text-slate-400 mt-1 text-sm">
            Configure how <strong className="text-slate-200">₹{expenseAmount.toFixed(2)}</strong> for <strong className="text-indigo-400">"{expense.title}"</strong> is split.
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Step 1: Select Members */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Step 1: Select Members Sharing</h3>
            <div className="flex space-x-3 text-xs">
              <button onClick={selectAll} className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">Select All</button>
              <span className="text-slate-700">|</span>
              <button onClick={selectNone} className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">Deselect All</button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 bg-slate-900/20 border border-slate-800/40 rounded-2xl p-4">
            {members.map(member => {
              const isSelected = selectedMemberIds.includes(member.id);
              return (
                <div 
                  key={member.id}
                  onClick={() => toggleMemberSelection(member.id)}
                  className={`flex items-center space-x-3 p-3 rounded-xl border cursor-pointer transition-all ${
                    isSelected 
                      ? 'bg-indigo-500/10 border-indigo-500/30 text-white' 
                      : 'border-slate-800/40 text-slate-400 hover:bg-slate-800/20'
                  }`}
                >
                  {isSelected ? (
                    <CheckSquare className="w-4 h-4 text-indigo-400" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-600" />
                  )}
                  <span className="text-sm font-medium">{member.name}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step 2: Choose Method */}
        <div>
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">Step 2: Choose Split Method</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => setSplitMethod('equal')}
              className={`py-3 rounded-xl border text-sm font-semibold transition-all ${
                splitMethod === 'equal'
                  ? 'bg-indigo-500/10 border-indigo-500/30 text-white shadow-lg shadow-indigo-500/5'
                  : 'border-slate-800/40 text-slate-400 hover:bg-slate-800/20'
              }`}
            >
              Split Equally
            </button>
            <button
              onClick={() => setSplitMethod('unequal')}
              className={`py-3 rounded-xl border text-sm font-semibold transition-all ${
                splitMethod === 'unequal'
                  ? 'bg-indigo-500/10 border-indigo-500/30 text-white shadow-lg shadow-indigo-500/5'
                  : 'border-slate-800/40 text-slate-400 hover:bg-slate-800/20'
              }`}
            >
              Split Unequally (Custom)
            </button>
          </div>
        </div>

        {/* Step 3: Configure Splits */}
        <div>
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">Step 3: Confirm Split Details</h3>
          
          {selectedMemberIds.length === 0 ? (
            <div className="text-center py-6 border border-dashed border-slate-800/50 rounded-2xl">
              <p className="text-slate-500 text-sm">Please select at least one member above.</p>
            </div>
          ) : splitMethod === 'equal' ? (
            /* Equal Split Details */
            <div className="space-y-4">
              {calculating ? (
                <div className="flex justify-center py-6">
                  <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
                </div>
              ) : (
                <div className="divide-y divide-slate-800/40 bg-slate-900/20 border border-slate-800/40 rounded-2xl px-5 py-2">
                  {equalPreview.map(p => (
                    <div key={p.member_id} className="py-3 flex justify-between items-center text-sm">
                      <span className="text-slate-300 font-medium">{p.member_name}</span>
                      <span className="font-bold text-white">₹{Number(p.amount).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* Unequal Split Details */
            <div className="space-y-4">
              <div className="space-y-3 bg-slate-900/20 border border-slate-800/40 rounded-2xl p-5">
                {members.filter(m => selectedMemberIds.includes(m.id)).map(member => (
                  <div key={member.id} className="flex justify-between items-center space-x-4">
                    <span className="text-slate-300 text-sm font-medium">{member.name}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-500 text-sm">₹</span>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={unequalAmounts[member.id] || ''}
                        onChange={(e) => setUnequalAmounts({
                          ...unequalAmounts,
                          [member.id]: e.target.value
                        })}
                        className="w-28 px-3 py-1.5 rounded-lg glass-input text-sm text-right"
                        placeholder="0.00"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Dynamic calculations display */}
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/50 flex flex-wrap justify-between items-center text-xs text-slate-400 gap-y-2">
                <div>
                  <span>Total Split: </span>
                  <span className="text-white font-bold">₹{unequalTotal.toFixed(2)}</span>
                  <span> of ₹{expenseAmount.toFixed(2)}</span>
                </div>
                
                {Math.abs(unequalDiff) < 0.01 ? (
                  <span className="text-emerald-400 font-semibold">Perfect split match!</span>
                ) : (
                  <span className={unequalDiff > 0 ? 'text-amber-400' : 'text-rose-400'}>
                    {unequalDiff > 0 
                      ? `Remaining to allocate: ₹${unequalDiff.toFixed(2)}` 
                      : `Exceeded by: ₹${Math.abs(unequalDiff).toFixed(2)}`
                    }
                  </span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <button
          onClick={handleSaveSplits}
          disabled={saving || (splitMethod === 'unequal' && Math.abs(unequalDiff) >= 0.01) || selectedMemberIds.length === 0}
          className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700/30 disabled:text-slate-500 text-white rounded-xl text-sm font-semibold transition-all flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/10 hover:shadow-indigo-500/20"
        >
          {saving ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <span>Save Splits Configuration</span>
          )}
        </button>
      </div>
    </div>
  );
}
