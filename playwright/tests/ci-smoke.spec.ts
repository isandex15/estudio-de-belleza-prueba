import { expect, test } from '@playwright/test';

const publicPages = [
  { path: '/', title: 'ATELYER GUIMAR' },
  { path: '/quienesomos', title: 'Quienes Somos Estudio De Belleza ATELYER GUIMAR' },
  { path: '/servicios', title: 'Estudio de belleza ATELYER GUIMAR' },
  { path: '/promociones', title: 'Promociones Estudio de Belleza ATELYER GUIMAR' },
];

for (const { path, title } of publicPages) {
  test(`@ci carga ${path}`, async ({ page }) => {
    const response = await page.goto(path);

    expect(response?.ok()).toBeTruthy();
    await expect(page).toHaveTitle(new RegExp(title, 'i'));
  });
}
