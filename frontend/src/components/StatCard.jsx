import React from 'react';

export default function StatCard({ title, value, icon: Icon, description, trend, trendColor = 'text-indigo-400' }) {
  return (
    <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold font-sans mt-2 tracking-tight text-white">{value}</h3>
        </div>
        <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400">
          <Icon className="w-6 h-6" />
        </div>
      </div>
      {description && (
        <div className="mt-4 flex items-center space-x-1.5 text-xs">
          {trend && <span className={`${trendColor} font-semibold`}>{trend}</span>}
          <span className="text-slate-500">{description}</span>
        </div>
      )}
    </div>
  );
}
