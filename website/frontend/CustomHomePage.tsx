import { HomePage } from '@usecross/docs'

export default function CustomHomePage(props: any) {
  return (
    <HomePage {...props}>
      <HomePage.Header />
      <HomePage.Hero />
      <HomePage.Features />
      <HomePage.CTA />
      <HomePage.Footer />
    </HomePage>
  )
}
