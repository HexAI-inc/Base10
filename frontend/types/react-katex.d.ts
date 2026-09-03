declare module 'react-katex' {
  import { ComponentType } from 'react'

  export interface KatexProps {
    children?: string
    math?: string
    block?: boolean
    errorColor?: string
    renderError?: (error: Error | TypeError) => React.ReactNode
    settings?: any
  }

  export const InlineMath: ComponentType<KatexProps>
  export const BlockMath: ComponentType<KatexProps>
}
