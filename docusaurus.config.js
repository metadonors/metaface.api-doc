module.exports = {
  title: 'Metaface API',
  tagline: 'Access your Face2Face platform APIs',
  url: 'https://metadonors.github.com',
  baseUrl: '/metaface.api-doc',
  favicon: 'img/favicon.png',
  organizationName: 'metadonors',
  projectName: 'metaface.api-doc',
  themeConfig: {
    navbar: {
      title: 'Metaface API',
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
              label: 'Style Guide',
              to: 'docs/doc1',
            },
            {
              label: 'Second Doc',
              to: 'docs/doc2',
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
      copyright: `Copyright © ${new Date().getFullYear()} Metadonors.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/facebook/docusaurus/edit/master/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
