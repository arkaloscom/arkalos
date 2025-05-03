import { ErrorBoundary } from '@/components/ErrorBoundary'
import Nav from '../components/Nav'

export default function MainLayout({ title, children, className = null }) {
  return (
    <>
      <title>{title}</title>
      <Nav />
      <main className={className}>{children}</main>
      <footer>
        Powered by Arkalos. We are grateful to the communities behind{' '}
        <a href="https://arkalos.com/appreciations/" target="_blank">
          these
        </a>{' '}
        open-source projects on which we depend.
      </footer>
    </>
  )
}
