import React, { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'

interface Option {
  value: string
  label: string
}

interface CustomSelectProps {
  value: string
  onChange: (value: string) => void
  options: Option[]
  placeholder: string
  icon?: React.ReactNode
}

const CustomSelect: React.FC<CustomSelectProps> = ({
  value,
  onChange,
  options,
  placeholder,
  icon
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [focusedIndex, setFocusedIndex] = useState(-1)
  const selectRef = useRef<HTMLDivElement>(null)
  const optionsRef = useRef<HTMLDivElement>(null)

  const selectedOption = options.find(option => option.value === value)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false)
        setFocusedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isOpen) {
      if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
        event.preventDefault()
        setIsOpen(true)
        setFocusedIndex(0)
      }
      return
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        setFocusedIndex(prev => 
          prev < options.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        event.preventDefault()
        setFocusedIndex(prev => prev > 0 ? prev - 1 : prev)
        break
      case 'Enter':
        event.preventDefault()
        if (focusedIndex >= 0) {
          onChange(options[focusedIndex].value)
          setIsOpen(false)
          setFocusedIndex(-1)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setFocusedIndex(-1)
        break
    }
  }

  const handleOptionClick = (optionValue: string) => {
    onChange(optionValue)
    setIsOpen(false)
    setFocusedIndex(-1)
  }

  return (
    <div 
      ref={selectRef}
      style={{
        position: 'relative',
        width: '100%',
        paddingLeft: 36, // под иконку
        paddingRight: 36, // симметричный отступ под стрелку
        boxSizing: 'border-box',
      }}
    >
      <div
        tabIndex={0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          width: '100%',
          padding: '16px',
          backgroundColor: 'white',
          border: `1px solid ${isOpen ? '#3b82f6' : '#e5e7eb'}`,
          borderRadius: '12px',
          color: selectedOption ? '#111827' : '#9ca3af',
          fontSize: '16px',
          cursor: 'pointer',
          outline: 'none',
          transition: 'all 0.2s ease',
          boxShadow: isOpen ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none'
        }}
        onMouseEnter={(e) => {
          if (!isOpen) {
            e.currentTarget.style.borderColor = '#d1d5db'
          }
        }}
        onMouseLeave={(e) => {
          if (!isOpen) {
            e.currentTarget.style.borderColor = '#e5e7eb'
          }
        }}
      >
        {icon && (
          <div style={{ flexShrink: 0 }}>
            {icon}
          </div>
        )}
        <span style={{ flex: 1, textAlign: 'left' }}>
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown 
          size={20} 
          style={{ 
            color: '#6b7280',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease'
          }} 
        />
      </div>

      {isOpen && (
        <div
          ref={optionsRef}
          role="listbox"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            width: '100%', // Используем width вместо left/right
            zIndex: 50,
            marginTop: '4px',
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            maxHeight: '200px',
            overflowY: 'auto'
          }}
        >
          {options.map((option, index) => (
            <div
              key={option.value}
              role="option"
              aria-selected={option.value === value}
              onClick={() => handleOptionClick(option.value)}
              style={{
                padding: '12px 16px',
                color: option.value === value ? '#2563eb' : '#111827',
                backgroundColor: index === focusedIndex ? '#f3f4f6' : 
                                option.value === value ? '#eff6ff' : 'transparent',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: option.value === value ? '500' : 'normal',
                borderRadius: index === 0 ? '12px 12px 0 0' : 
                            index === options.length - 1 ? '0 0 12px 12px' : '0',
                transition: 'all 0.1s ease'
              }}
              onMouseEnter={(e) => {
                setFocusedIndex(index)
                if (option.value !== value) {
                  e.currentTarget.style.backgroundColor = '#f9fafb'
                }
              }}
              onMouseLeave={(e) => {
                if (option.value !== value && index !== focusedIndex) {
                  e.currentTarget.style.backgroundColor = 'transparent'
                }
              }}
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CustomSelect
