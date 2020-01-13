module.exports = {
  title: 'Metaface for Developers',
  tagline: 'Access your Face2Face platform APIs',
  url: 'https://stupefied-meitner-bdd174.netlify.com/',
  baseUrl: '/',
  favicon: 'img/favicon.png',
  organizationName: 'metadonors',
  projectName: 'metaface.api-doc',
  themeConfig: {
    navbar: {
      title: 'Metaface for Developers',
      logo: {
        alt: 'Metaface',
        src: 'img/logo.png',
      },
      links: [
        {to: 'docs/overview', label: 'Docs', position: 'left'}
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: 'docs/overview',
            },
            {
              label: 'Reference',
              to: 'docs/signups',
            },
          ],
        },
        {
          title: 'Websites',
          items: [
            {
              label: 'Metaface',
              href: 'https://metaface.io',
            },
            {
              label: 'Metadonors',
              href: 'https://metadonors.it',
            },
          ],
        },
        {
          title: 'Social',
          items: [
            {
              label: 'Blog',
              href: 'https://academy.metadonors.it',
            }
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Metadonors`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
