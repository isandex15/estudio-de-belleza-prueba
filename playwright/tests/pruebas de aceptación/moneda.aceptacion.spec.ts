import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from '../auth';
import { baseUrl, uniqueLetters } from './helpers';

type AlertResponse = {
  icon?: string;
  text?: string;
};

test('Moneda: crear, editar y eliminar un registro temporal', async ({
  page,
}) => {
  // CP-MON-23: Registra, edita y elimina una moneda temporal.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Moneda.
  await abrirModulo(page, 'moneda');

  const suffix = uniqueLetters();
  const originalName = `Test${suffix}`;
  const updatedName = `Edit${suffix}`;
  let cleanupId: string | undefined;

  try {
    // 3. Registrar una moneda temporal.
    await page.getByRole('button', { name: 'Registrar Moneda' }).click();
    await page.locator('#nombre_moneda').fill(originalName);

    const createResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=moneda') &&
        request.method() === 'POST' &&
        request.postData()?.includes('registrar=1') === true
      );
    });
    await page
      .locator('#modalRegistrarMoneda')
      .getByRole('button', { name: 'Guardar' })
      .click();

    const created: AlertResponse = await (await createResponse).json();
    expect(created.icon).toBe('success');

    const row = page.locator('#table1 tbody tr').filter({ hasText: originalName });
    await expect(row).toHaveCount(1);
    cleanupId = (await row.locator('td').first().innerText()).trim();

    // 4. Editar el registro temporal.
    await row.locator('button[title="Editar"]').click();
    const editModal = page.locator('#editModal');
    await expect(editModal).toBeVisible();
    await page.locator('#edit_nombre_moneda').fill(updatedName);
    await page.locator('#edit_estado').selectOption('1');

    const updateResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=moneda') &&
        request.method() === 'POST' &&
        request.postData()?.includes('actualizar=1') === true
      );
    });
    await editModal.getByRole('button', { name: 'Editar' }).click();
    const updated: AlertResponse = await (await updateResponse).json();
    expect(updated.icon).toBe('success');

    const updatedRow = page
      .locator('#table1 tbody tr')
      .filter({ hasText: updatedName });
    await expect(updatedRow).toHaveCount(1);

    // 5. Eliminar el registro temporal.
    await updatedRow.locator('button[title="Eliminar"]').click();
    const deleteModal = page.locator('#deleteModal');
    await expect(deleteModal).toBeVisible();

    const deleteResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=moneda') &&
        request.method() === 'POST' &&
        request.postData()?.includes('eliminar=1') === true
      );
    });
    await deleteModal.getByRole('button', { name: 'Eliminar' }).click();
    const deleted: AlertResponse = await (await deleteResponse).json();
    expect(deleted.icon).toBe('success');
    cleanupId = undefined;

    await expect(updatedRow).toHaveCount(0);
  } finally {
    // 6. Limpiar el registro si el flujo falla antes de eliminarlo.
    if (cleanupId) {
      const response = await page.context().request.post(
        `${baseUrl}/admin?ruta=moneda`,
        { form: { eliminar: '1', cod_moneda: cleanupId } }
      );
      if (!response.ok()) {
        throw new Error('No se pudo limpiar la moneda temporal.');
      }
      const result: AlertResponse = await response.json();
      if (result.icon !== 'success') {
        throw new Error(result.text ?? 'No se pudo limpiar la moneda temporal.');
      }
    }
  }
});
