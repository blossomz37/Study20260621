// Generated from DESIGN.md by tools/designmd-export — do not edit by hand.
/** @type {import('tailwindcss').Config} */
module.exports = {
  "theme": {
    "extend": {
      "colors": {
        "primary": "#5b21b6",
        "primary-strong": "#4c1d95",
        "on-primary": "#f5f3ff",
        "secondary": "#2563eb",
        "tertiary": "#db2777",
        "accent": "#f59e0b",
        "surface": "#0b1020",
        "on-surface": "#eef0fb",
        "on-surface-variant": "#c7cbe0",
        "glass-fill": "rgba(255,255,255,0.10)",
        "glass-fill-strong": "rgba(255,255,255,0.16)",
        "glass-border": "rgba(255,255,255,0.22)",
        "glass-shadow": "rgba(8,10,25,0.45)"
      },
      "borderRadius": {
        "md": "12px",
        "lg": "20px",
        "full": "9999px"
      },
      "spacing": {
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "64px"
      },
      "fontFamily": {
        "sora": [
          "Sora",
          "sans-serif"
        ],
        "inter": [
          "Inter",
          "sans-serif"
        ]
      },
      "fontSize": {
        "display-lg": [
          "44px",
          {
            "lineHeight": "1.08",
            "fontWeight": "700",
            "letterSpacing": "-0.02em"
          }
        ],
        "title-md": [
          "22px",
          {
            "lineHeight": "1.2",
            "fontWeight": "600"
          }
        ],
        "body-lg": [
          "17px",
          {
            "lineHeight": "1.6",
            "fontWeight": "400"
          }
        ],
        "label-caps": [
          "12px",
          {
            "lineHeight": "1.2",
            "fontWeight": "600",
            "letterSpacing": "0.12em"
          }
        ]
      },
      "transitionDuration": {},
      "transitionTimingFunction": {},
      "transitionProperty": {},
      "backgroundImage": {
        "hero": "linear-gradient(135deg, var(--color-primary) 0%, var(--color-tertiary) 55%, var(--color-accent) 100%)"
      },
      "backdropBlur": {
        "glass": "20px",
        "glass-strong": "40px"
      },
      "boxShadow": {
        "glass": "0 8px 32px 0 var(--color-glass-shadow)"
      }
    }
  }
};
