import MainLayout from '@/layouts/MainLayout'

export default function IndexPage() {
  return (
    <MainLayout title="Home" className="index">
      <img
        src="https://arkalos.com/assets/img/arkalos-logo.png"
        alt="Arkalos Logo"
        style={{ width: '15rem', marginBottom: '3rem' }}
      />
      <h1 style={{ fontSize: '5rem', marginBottom: '5rem' }}>Ship beautiful data</h1>
      <section style={{ display: 'flex', gap: '4rem', fontSize: '2rem', marginBottom: '7rem' }}>
        <a href="https://arkalos.com" target="_blank">
          Documentation
        </a>
        <a href="https://github.com/arkaloscom/arkalos/" target="_blank">
          Star us on GitHub
        </a>
        <a href="https://x.com/i/communities/1889982611667534002/" target="_blank">
          Join Community
        </a>
      </section>
    </MainLayout>
  )
}
