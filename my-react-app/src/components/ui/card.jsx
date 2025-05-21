import React from "react";

export const Card = ({ children, className }) => {
  return (
    <div className={`p-4 border rounded shadow-md ${className}`}>
      {children}
    </div>
  );
};

export const CardContent = ({ children }) => {
  return <div className="mt-2">{children}</div>;
};
