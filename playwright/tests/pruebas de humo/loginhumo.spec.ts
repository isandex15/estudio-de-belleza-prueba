
import { test, expect } from '@playwright/test';

test('humo completo del módulo Inicio de Sesión', async ({ page }) => {
    await page.goto('http://localhost:5000/admin?ruta=login');

    // 1. CARGA DEL INICIO DE SESIÓN
    const formularioLogin = page.locator('#loginForm');

    await expect(formularioLogin).toBeVisible();
    await expect(formularioLogin.locator('input[name="cedula"]')).toBeVisible();
    await expect(formularioLogin.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('#loginButton')).toBeVisible();


    // 2. CAPTCHA
    await page.locator('#pow-open').click();

    const panelCaptcha = page.locator('#pow-panel');

    await expect(panelCaptcha).toBeVisible();
    await expect(page.locator('#pow-answer')).toBeVisible();
    await expect(page.locator('#pow-verify')).toBeVisible();

    await page.locator('#pow-answer').fill('AB12CD');
    await page.locator('#pow-verify').click();


    // 3. OLVIDASTE LA CONTRASEÑA
    await page.locator('#forgot-password-link').click();

    const formularioRestablecer = page.locator('#resetPasswordContainer');

    await expect(formularioRestablecer).toBeVisible();
    await expect(formularioRestablecer.locator('#resetPasswordForm')).toBeVisible();
    await expect(formularioRestablecer.locator('input[name="cedula"]')).toBeVisible();
    await expect(formularioRestablecer.locator('#newPassword')).toBeVisible();
    await expect(formularioRestablecer.locator('#confirmPassword')).toBeVisible();

    console.log('Formulario para restablecer contraseña cargado correctamente');

    await page.locator('#back-to-login-reset').click();
    await expect(formularioLogin).toBeVisible();
    console.log(' prueba finaliza ');
});
