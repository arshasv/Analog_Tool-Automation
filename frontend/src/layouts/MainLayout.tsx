import Navbar from '@components/Navbar'
import React from 'react'
import './MainLayout.css'

interface MainLayoutProps {
  children: React.ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="main-layout">
      <Navbar />
      <main className="layout-main">{children}</main>
    </div>
  )
}
