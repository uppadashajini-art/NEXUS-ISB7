/**
 * NEXUS Foundation Tailwind Theme Extension
 * Enterprise tokens matching tokens.css exactly
 */
export const nexusTailwindTheme = {
  extend: {
    fontFamily: {
      sans: ['Montserrat', 'sans-serif'],
      mono: ['Montserrat', 'sans-serif'], // All fonts strictly Montserrat
    },
    colors: {
      nexus: {
        bg: '#0B0B0E',
        surface: '#121217',
        'surface-2': '#17171E',
        border: 'rgba(255, 255, 255, 0.07)',
        'border-strong': 'rgba(255, 255, 255, 0.12)',
        text: {
          primary: '#F5F5F7',
          secondary: '#A1A1AA',
          tertiary: '#6B6B76',
        },
        accent: {
          idea: '#FFC72C',
          market: '#FF8A1F',
          customer: '#FF5A4E',
          competitor: '#F23D5C',
          feasibility: '#2DD4BF',
          advisory: '#8B7CF6',
        },
      },
    },
    backgroundImage: {
      'brand-gradient': 'linear-gradient(135deg, #FFC72C 0%, #FF8A1F 50%, #F23D5C 100%)',
    },
    spacing: {
      '1': '4px',
      '2': '8px',
      '3': '12px',
      '4': '16px',
      '5': '20px',
      '6': '24px',
      '8': '32px',
      '10': '40px',
      '12': '48px',
      '16': '64px',
    },
    borderRadius: {
      sm: '8px',
      md: '12px',
      lg: '16px',
      xl: '24px',
    },
    boxShadow: {
      'elevation-1': '0 1px 2px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(255, 255, 255, 0.07)',
      'elevation-2': '0 4px 12px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.07)',
      'elevation-3': '0 12px 32px rgba(0, 0, 0, 0.60), 0 0 0 1px rgba(255, 255, 255, 0.12)',
    },
    transitionDuration: {
      150: '150ms',
      250: '250ms',
      400: '400ms',
    },
    transitionTimingFunction: {
      nexus: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
    },
  },
};

export default nexusTailwindTheme;
