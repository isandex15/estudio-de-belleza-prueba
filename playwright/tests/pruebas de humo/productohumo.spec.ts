import { expect, test } from '@playwright/test';
import {
  abrirModuloAdmin,
  confirmarAlerta,
  eliminarFila,
  fechaRelativa,
  filaPorTexto,
  nombreDePrueba,
} from '../admin-test-support';

test('humo del módulo de productos', async ({ page }) => {
  await abrirModuloAdmin(page, 'producto', 'Productos (Inventario)');

  await expect(page.locator('#table1 thead')).toContainText('Código');
  await expect(page.locator('#table1 thead')).toContainText('Nombre');

  const nombre = nombreDePrueba('Producto', 18);
  await page.getByRole('button', { name: 'Registrar Producto' }).click();

  const modal = page.locator('#modalRegistrar');
  await expect(modal).toBeVisible();
  await page.locator('#nombre_producto').fill(nombre);
  await page.locator('#precio_producto').fill('10.50');
  await page.locator('#stock').fill('5');
  await page.locator('#fecha_vencimiento').fill(fechaRelativa(30));

  for (const selector of [
    '#cod_marca',
    '#cod_categoria',
    '#cod_unidad',
    '#cod_presentacion',
    '#cod_tipo_producto',
    '#cod_medida',
  ]) {
    await page.locator(selector).selectOption({ index: 0 });
  }

  await page.locator('#formRegistrarProducto button[type="submit"]').click();
  await confirmarAlerta(page);

  const fila = await filaPorTexto(page, nombre);
  await eliminarFila(
    page,
    fila,
    'button[data-bs-target="#modalEliminar"]',
    '#modalEliminar',
    '#formEliminarProducto button.btn-danger',
  );
});
