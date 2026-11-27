import { randomInt } from 'node:crypto';

import { expect, test } from '@playwright/test';

import { abrirModulo, iniciarSesion } from '../pruebas de interfaz/auth';
import { baseUrl, uniqueLetters } from './helpers';

type AlertResponse = {
  icon?: string;
  text?: string;
};

test('Personal: registrar, editar y eliminar lógicamente un usuario temporal', async ({
  page,
}) => {
  // CP-PER-31: Registra, edita y elimina lógicamente personal temporal.

  // 1. Iniciar sesión.
  await iniciarSesion(page);

  // 2. Acceder al módulo Personal.
  await abrirModulo(page, 'personal');

  const suffix = uniqueLetters();
  const cedula = String(randomInt(10000000, 99999999));
  const email = `prueba${suffix.toLowerCase()}@gmail.com`;
  let cleanupNeeded = false;

  try {
    // 3. Registrar personal temporal.
    await page.getByRole('button', { name: 'Registrar Personal' }).click();
    await page.locator('#cedula_reg').fill(cedula);
    await page.locator('#nombre_usuario_reg').fill(`Prueba${suffix}`);
    await page.locator('#apellido_usuario_reg').fill('Aceptacion');
    await page.locator('#telefono_reg').fill(`0412${randomInt(100000, 999999)}`);
    await page.locator('#direccion_reg').fill('Av Prueba 123');
    await page.locator('#correo_reg').fill(email);

    const createResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=personal') &&
        request.method() === 'POST' &&
        request.postData()?.includes('registrar=1') === true
      );
    });
    await page
      .locator('#modalRegistrarPersonal')
      .getByRole('button', { name: 'Guardar' })
      .click();

    const created: AlertResponse = await (await createResponse).json();
    expect(created.icon).toBe('success');
    cleanupNeeded = true;

    const row = page.locator('#table1 tbody tr').filter({ hasText: cedula });
    await expect(row).toHaveCount(1);

    // 4. Editar el registro temporal.
    await row.locator('button[title="Editar"]').click();

    const editModal = page.locator('#modalEditar');
    await expect(editModal).toBeVisible();
    await page.locator('#nombre_usuario_edit').fill(`Editado${suffix}`);
    await page.locator('#apellido_usuario_edit').fill('Aceptado');
    await page.locator('#correo_edit').fill(email);

    const updateResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=personal') &&
        request.method() === 'POST' &&
        request.postData()?.includes('actualizar=1') === true
      );
    });
    await editModal.getByRole('button', { name: 'Editar' }).click();
    const updated: AlertResponse = await (await updateResponse).json();
    expect(updated.icon).toBe('success');

    const updatedRow = page.locator('#table1 tbody tr').filter({ hasText: cedula });
    await expect(updatedRow).toContainText(`Editado${suffix}`);

    // 5. Eliminar lógicamente el registro temporal.
    await updatedRow.locator('button[title="Eliminar"]').click();

    const deleteModal = page.locator('#modalEliminarPersonal');
    await expect(deleteModal).toBeVisible();

    const deleteResponse = page.waitForResponse((response) => {
      const request = response.request();
      return (
        response.url().includes('/admin?ruta=personal') &&
        request.method() === 'POST' &&
        request.postData()?.includes('eliminar=1') === true
      );
    });
    await deleteModal.getByRole('button', { name: 'Eliminar' }).click();
    const deleted: AlertResponse = await (await deleteResponse).json();
    expect(deleted.icon).toBe('success');
    cleanupNeeded = false;

    await expect(updatedRow).toHaveCount(0);
  } finally {
    // 6. Limpiar el registro si el flujo falla antes de eliminarlo.
    if (cleanupNeeded) {
      const response = await page.context().request.post(
        `${baseUrl}/admin?ruta=personal`,
        { form: { eliminar: '1', cedula } }
      );
      if (!response.ok()) {
        throw new Error('No se pudo limpiar el usuario temporal.');
      }
      const result: AlertResponse = await response.json();
      if (result.icon !== 'success') {
        throw new Error(result.text ?? 'No se pudo limpiar el usuario temporal.');
      }
    }
  }
});
