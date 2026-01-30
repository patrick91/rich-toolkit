import { HomePage } from '@usecross/docs'

export default function CustomHomePage(props: any) {
  // Provide default values for missing props
  const homePageProps = {
    ...props,
    navLinks: props.navLinks || [],
  }

  return (
    <HomePage {...homePageProps}>
      <HomePage.Header />
      <HomePage.Hero />
      <HomePage.Features />
      <HomePage.CTA />
      <HomePage.Footer />
    </HomePage>
  )
}
