import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMemberLedger } from '../services/api';
import { ArrowLeft, User, CreditCard, Scale, Calendar, AlertCircle } from 'lucide-react';

export default function MemberHistory() {
  const { groupId, memberId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadLedger = async () => {
      try {
        const response = await getMemberLedger(groupId, memberId);
        setData(response.data);
      } catch (err) {
        setError('Failed to fetch member ledger history details.');
      } finally {
        setLoading(false);
      }
    };
    loadLedger();
  }, [groupId, memberId]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-white">Error</h2>
        <p className="text-slate-400 mt-2">{error || 'Ledger details not found.'}</p>
        <Link to={`/groups/${groupId}`} className="text-indigo-400 hover:text-indigo-300 font-medium mt-4 inline-flex items-center space-x-1">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Group</span>
        </Link>
      </div>
    );
  }

  const { member, summary, expenses_paid, splits_owed, settlements_sent, settlements_received } = data;
  const netBalance = Number(summary?.net_balance || 0);
  const isOwedTo = netBalance > 0;
  const isOwed = netBalance < 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <Link to={`/groups/${groupId}`} className="text-indigo-400 hover:text-indigo-300 font-semibold mb-2 inline-flex items-center space-x-1 text-sm transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Group</span>
        </Link>
        <div className="flex items-center space-x-3 mt-1">
          <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
            <User className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight font-sans">
              {member.name}
            </h1>
            <p className="text-slate-400 text-sm mt-0.5">{member.email || 'No email associated'}</p>
          </div>
        </div>
      </div>

      {/* Net Summary Panel */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        <div className="glass-panel rounded-2xl p-5">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Paid Bills Total</p>
          <p className="text-2xl font-bold text-white mt-1.5">₹{Number(summary?.paid || 0).toFixed(2)}</p>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Owes Share Total</p>
          <p className="text-2xl font-bold text-white mt-1.5">₹{Number(summary?.owes || 0).toFixed(2)}</p>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Settled/Receivables</p>
          <p className="text-2xl font-bold text-white mt-1.5">₹{Number(summary?.receivable || 0).toFixed(2)}</p>
        </div>
        <div className={`glass-panel rounded-2xl p-5 border ${
          isOwedTo ? 'border-emerald-500/20 bg-emerald-500/5' : isOwed ? 'border-rose-500/20 bg-rose-500/5' : 'border-slate-800/40'
        }`}>
          <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Net Position</p>
          <p className={`text-2xl font-bold mt-1.5 ${
            isOwedTo ? 'text-emerald-400' : isOwed ? 'text-rose-400' : 'text-slate-200'
          }`}>
            {isOwedTo ? `+₹${netBalance.toFixed(2)}` : isOwed ? `-₹${Math.abs(netBalance).toFixed(2)}` : '₹0.00'}
          </p>
        </div>
      </div>

      {/* History Ledger Listings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Paid Bills Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white font-sans flex items-center space-x-2">
            <CreditCard className="w-5 h-5 text-indigo-400" />
            <span>Expenses Paid</span>
          </h2>

          {expenses_paid.length === 0 ? (
            <p className="text-slate-500 text-xs py-4">No expenses paid by this member.</p>
          ) : (
            <div className="space-y-3">
              {expenses_paid.map(exp => (
                <div key={exp.id} className="glass-panel rounded-xl p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-slate-200 text-sm">{exp.title}</h4>
                    <span className="text-[10px] text-slate-500 flex items-center space-x-1 mt-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(exp.date).toLocaleDateString()}</span>
                    </span>
                  </div>
                  <span className="font-bold text-white text-sm">₹{Number(exp.amount).toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Splits Owed Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white font-sans flex items-center space-x-2">
            <Scale className="w-5 h-5 text-indigo-400" />
            <span>Splits Owed (Debts)</span>
          </h2>

          {splits_owed.length === 0 ? (
            <p className="text-slate-500 text-xs py-4">No splits debt recorded for this member.</p>
          ) : (
            <div className="space-y-3">
              {splits_owed.map(split => (
                <div key={split.id} className="glass-panel rounded-xl p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-slate-200 text-sm">Debt split contribution</h4>
                    <span className="text-[10px] text-slate-500 flex items-center space-x-1 mt-1">
                      <Calendar className="w-3 h-3" />
                      <span>Split entry</span>
                    </span>
                  </div>
                  <span className="font-bold text-rose-400 text-sm">₹{Number(split.amount).toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settlements Sent */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white font-sans flex items-center space-x-2">
            <Scale className="w-5 h-5 text-rose-400" />
            <span>Settlements Sent (Payments Out)</span>
          </h2>

          {settlements_sent.length === 0 ? (
            <p className="text-slate-500 text-xs py-4">No outbound settlements recorded.</p>
          ) : (
            <div className="space-y-3">
              {settlements_sent.map(set => (
                <div key={set.id} className="glass-panel rounded-xl p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-slate-200 text-sm">Sent to {set.payee_name}</h4>
                    <span className="text-[10px] text-slate-500 flex items-center space-x-1 mt-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(set.date).toLocaleDateString()}</span>
                    </span>
                  </div>
                  <span className="font-bold text-rose-400 text-sm">₹{Number(set.amount).toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settlements Received */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white font-sans flex items-center space-x-2">
            <Scale className="w-5 h-5 text-emerald-400" />
            <span>Settlements Received (Payments In)</span>
          </h2>

          {settlements_received.length === 0 ? (
            <p className="text-slate-500 text-xs py-4">No inbound settlements received.</p>
          ) : (
            <div className="space-y-3">
              {settlements_received.map(set => (
                <div key={set.id} className="glass-panel rounded-xl p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-slate-200 text-sm">Received from {set.payer_name}</h4>
                    <span className="text-[10px] text-slate-500 flex items-center space-x-1 mt-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(set.date).toLocaleDateString()}</span>
                    </span>
                  </div>
                  <span className="font-bold text-emerald-400 text-sm">₹{Number(set.amount).toFixed(2)}</span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
