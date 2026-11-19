import React from 'react';

export default function SectionEyebrow({ label, rightAction }) {
  return (
    <div className="flex items-center justify-between border-b border-[#d8d8d8] pb-2 mb-4">
      <div className="flex items-center">
        <span className="w-2 h-5 bg-[#fa9000] mr-2.5 inline-block" />
        <h2 className="text-xl font-light uppercase tracking-wider text-[#595959]">
          {label}
        </h2>
      </div>
      {rightAction && (
        <div>{rightAction}</div>
      )}
    </div>
  );
}
