import { expect, type Page } from '@playwright/test';

const baseUrl = (
  process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5000'
).replace(/\/$/, '');

export async function iniciarSesion(page: Page): Promise<void> {
  const cedula = process.env.PLAYWRIGHT_USER_CEDULA;
  const password = process.env.PLAYWRIGHT_PASSWORD;

  if (!cedula || !password) {
    throw new Error(
      'Configura PLAYWRIGHT_USER_CEDULA y PLAYWRIGHT_PASSWORD para iniciar sesión.'
    );
  }

  await page.goto(`${baseUrl}/admin?ruta=login`);
  await page.getByRole('textbox', { name: 'Cédula' }).fill(cedula);
  await page.locator('#login-password').fill(password);
  await page.locator('#pow-check').click();
  await expect(page.locator('#pow-image')).toBeVisible();
  const captchaAnswer = page.locator('#pow-answer');
  await expect(captchaAnswer).toBeEnabled();
  await captchaAnswer.fill(process.env.PLAYWRIGHT_CAPTCHA_CODE ?? 'AB12CD');

  const captchaVerification = page.waitForResponse((response) => {
    const request = response.request();
    return (
      response.url().includes('/admin?ruta=login') &&
      request.method() === 'POST' &&
      request.postData()?.includes('verificar_captcha=1') === true
    );
  });
  await page.locator('#pow-verify').click();
  const captchaResponse = await captchaVerification;
  const captchaResult: { verificado?: boolean } = await captchaResponse.json();
  if (!captchaResult.verificado) {
    throw new Error('No se pudo verificar el CAPTCHA de prueba.');
  }

  const loginResponsePromise = page.waitForResponse((response) => {
    const request = response.request();
    return (
      response.url().includes('/admin?ruta=login') &&
      request.method() === 'POST' &&
      request.postData()?.includes('login=') === true
    );
  });
  await page.locator('#loginButton').click();
  const loginResponse = await loginResponsePromise;
  const loginResult: { redirect?: string; text?: string } =
    await loginResponse.json();
  if (!loginResult.redirect) {
    throw new Error(loginResult.text ?? 'No se pudo iniciar sesión.');
  }

  await expect(page.locator('.sidebar-menu')).toBeVisible({
    timeout: 15000,
  });
}

export async function abrirModulo(page: Page, ruta: string): Promise<void> {
  await page.goto(`${baseUrl}/admin?ruta=${ruta}`);
  await expect(page.locator('section[data-modulo]')).toBeVisible({
    timeout: 15000,
  });
}
