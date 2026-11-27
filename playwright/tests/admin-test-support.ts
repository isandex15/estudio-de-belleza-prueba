// @ts-check
import { expect, type Locator, type Page } from '@playwright/test';

export async function abrirModuloAdmin(page: Page, ruta: string, titulo: string) {
  await page.goto('http://localhost:5000/admin?ruta=login');
  await page.getByRole('textbox', { name: 'Cédula' }).fill('4723317');
  await page.getByRole('textbox', { name: 'Password' }).fill('admin123');
  await page.locator('#pow-open').click();
  await page.locator('#pow-answer').fill('AB12CD');
  await page.locator('#pow-verify').click();
  await page.locator('#loginButton').click();
  await expect(page.getByRole('heading', { name: 'Bienvenido' })).toBeVisible();

  await page.goto(`http://localhost:5000/admin?ruta=${ruta}`);
  await expect(page.getByRole('heading', { name: titulo })).toBeVisible();
  await expect(page.locator('#table1')).toBeVisible();
}

export function sufijoUnico(): string {
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`
    .replace(/[0-9]/g, (digit) => String.fromCharCode(97 + Number(digit)));
}

export function nombreDePrueba(prefijo: string, maxLength = 20): string {
  return `${prefijo}${sufijoUnico()}`.slice(0, maxLength);
}

export function numeroDePrueba(length: number): string {
  return Array.from({ length }, () => Math.floor(Math.random() * 10)).join('');
}

export function fechaRelativa(dias: number): string {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + dias);
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const dia = String(fecha.getDate()).padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
}

export async function confirmarAlerta(page: Page): Promise<void> {
  const botonAceptar = page.locator('.swal2-confirm');
  await expect(botonAceptar).toBeVisible();
  await botonAceptar.click();
}

export async function assertInputInvalido(page: Page, selector: string): Promise<void> {
  const campo = page.locator(selector);
  await expect(campo).toHaveClass(/is-invalid/);
  await expect(
    campo.locator('xpath=following-sibling::div[contains(@class, "invalid-feedback")]').first(),
  ).toBeVisible();
}

export async function filaPorTexto(page: Page, texto: string): Promise<Locator> {
  const fila = page.locator('#table1 tbody tr').filter({ hasText: texto });
  await expect(fila).toBeVisible();
  return fila;
}

export async function buscarFila(page: Page, texto: string): Promise<Locator> {
  const buscador = page.locator('#table1_filter input');
  await expect(buscador).toBeVisible();
  await buscador.fill(texto);

  const fila = page.locator('#table1 tbody tr').filter({ hasText: texto });
  await expect(fila).toBeVisible();
  await expect(fila).toHaveCount(1);

  await buscador.fill('');
  await expect(fila).toBeVisible();
  return fila;
}

export async function eliminarFila(
  page: Page,
  fila: Locator,
  botonEliminar: string,
  modalSelector: string,
  botonConfirmar: string,
): Promise<void> {
  await fila.locator(botonEliminar).click();
  const modal = page.locator(modalSelector);
  await expect(modal).toBeVisible();
  await page.locator(botonConfirmar).click();
  await confirmarAlerta(page);
  await expect(modal).toBeHidden();
  await expect(fila).toHaveCount(0);
}
