const API = "/v1/api";

const sesion = {
    token: sessionStorage.getItem("token"),
    usuario: JSON.parse(sessionStorage.getItem("usuario") || "null"),
};
let productos = [];
// Cada línea del pedido: { producto_id, cantidad, notas }
let carrito = [];

const $ = (selector) => document.querySelector(selector);
const dinero = (valor) => `$${Number(valor).toFixed(2)}`;
const fecha = (texto) => new Date(texto).toLocaleString("es-MX", { dateStyle: "short", timeStyle: "short" });
const esAdmin = () => sesion.usuario?.rol === "admin";

// Evita inyección de HTML al pintar datos que vienen de la API o que escribe el usuario
const ENTIDADES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
const esc = (texto) => String(texto ?? "").replace(/[&<>"']/g, (c) => ENTIDADES[c]);

async function api(ruta, { method = "GET", json, form } = {}) {
    const headers = {};
    let body;
    if (sesion.token) headers.Authorization = `Bearer ${sesion.token}`;
    if (json !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(json);
    }
    if (form) body = new URLSearchParams(form);

    const respuesta = await fetch(API + ruta, { method, headers, body });
    const datos = await respuesta.json().catch(() => null);

    if (respuesta.status === 401 && sesion.token) {
        cerrarSesion();
        throw new Error("Tu sesión expiró. Inicia sesión de nuevo.");
    }
    if (!respuesta.ok) throw new Error(mensajeError(datos));
    return datos;
}

function mensajeError(datos) {
    if (!datos?.detail) return "Ocurrió un error inesperado.";
    if (typeof datos.detail === "string") return datos.detail;
    return datos.detail.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(" | ");
}

function avisar(mensaje, error = false) {
    const aviso = $("#aviso");
    aviso.textContent = mensaje;
    aviso.className = error ? "aviso error" : "aviso";
    clearTimeout(avisar.temporizador);
    avisar.temporizador = setTimeout(() => aviso.classList.add("oculto"), 4500);
}

async function ejecutar(accion) {
    try {
        await accion();
    } catch (error) {
        avisar(error.message, true);
    }
}

function pedir(texto, valor = "") {
    const dialogo = $("#dialogo");
    const input = $("#dialogo-input");
    $("#dialogo-texto").textContent = texto;
    input.value = valor;
    dialogo.returnValue = "";
    dialogo.showModal();
    input.select();
    return new Promise((resolver) => {
        dialogo.onclose = () => resolver(dialogo.returnValue === "ok" ? input.value : null);
    });
}

$("#dialogo-cancelar").addEventListener("click", () => $("#dialogo").close());

// Sesión
function mostrarErrorLogin(mensaje) {
    const alerta = $("#login-alerta");
    const tarjeta = $(".login-card-container");
    if (alerta) {
        alerta.textContent = mensaje;
        alerta.classList.remove("oculto");
    }
    if (tarjeta) {
        tarjeta.classList.remove("shake");
        void tarjeta.offsetWidth;
        tarjeta.classList.add("shake");
    }
}

const btnTogglePass = $("#btn-toggle-pass");
if (btnTogglePass) {
    btnTogglePass.addEventListener("click", () => {
        const passInput = $("#input-password");
        if (!passInput) return;
        const esPass = passInput.type === "password";
        passInput.type = esPass ? "text" : "password";
        $(".icono-ojo")?.classList.toggle("oculto", esPass);
        $(".icono-ojo-tachado")?.classList.toggle("oculto", !esPass);
    });
}

$("#form-login").addEventListener("submit", (evento) => {
    evento.preventDefault();
    $("#login-alerta")?.classList.add("oculto");

    const btnSubmit = $("#btn-login-submit");
    const txtSubmit = btnSubmit?.querySelector(".btn-texto");
    const spinner = btnSubmit?.querySelector(".spinner-carga");

    if (btnSubmit) btnSubmit.disabled = true;
    if (txtSubmit) txtSubmit.textContent = "Verificando...";
    if (spinner) spinner.classList.remove("oculto");

    ejecutar(async () => {
        try {
            const datos = await api("/auth/login", { method: "POST", form: new FormData(evento.target) });
            sesion.token = datos.access_token;
            sesion.usuario = datos.usuario;
            sessionStorage.setItem("token", sesion.token);
            sessionStorage.setItem("usuario", JSON.stringify(sesion.usuario));
            evento.target.reset();
            mostrarApp();
        } catch (error) {
            mostrarErrorLogin(error.message || "Usuario o contraseña incorrectos");
            throw error;
        } finally {
            if (btnSubmit) btnSubmit.disabled = false;
            if (txtSubmit) txtSubmit.textContent = "Ingresar al Sistema";
            if (spinner) spinner.classList.add("oculto");
        }
    });
});

$("#btn-salir").addEventListener("click", cerrarSesion);

function cerrarSesion() {
    sesion.token = null;
    sesion.usuario = null;
    sessionStorage.clear();
    carrito = [];
    $("#login-alerta")?.classList.add("oculto");
    $("#vista-app").classList.add("oculto");
    $("#vista-login").classList.remove("oculto");
}

function mostrarApp() {
    $("#vista-login").classList.add("oculto");
    $("#vista-app").classList.remove("oculto");
    document.body.classList.toggle("es-cajero", !esAdmin());
    $("#nombre-usuario").textContent = `${sesion.usuario.nombre} (${sesion.usuario.rol})`;
    cambiarVista("pedido");
}

// Navegación
const cargadores = {
    pedido: cargarMenu,
    pedidos: cargarPedidos,
    inventario: cargarInventario,
    productos: cargarProductos,
    usuarios: cargarUsuarios,
    reportes: cargarReportes,
};

document.querySelectorAll("nav button").forEach((boton) => {
    boton.addEventListener("click", () => cambiarVista(boton.dataset.vista));
});

function cambiarVista(nombre) {
    document.querySelectorAll(".vista").forEach((vista) => vista.classList.add("oculto"));
    document.querySelectorAll("nav button").forEach((b) => b.classList.toggle("activo", b.dataset.vista === nombre));
    $(`#vista-${nombre}`).classList.remove("oculto");
    ejecutar(cargadores[nombre]);
}

// Nuevo pedido
async function cargarMenu() {
    productos = await api("/productos");
    $("#menu").innerHTML = productos.map((p) => `
        <div class="producto">
            <strong>${esc(p.nombre)}</strong>
            <span class="tenue pequeno">${esc(p.descripcion)}</span>
            <span class="precio">${p.precio === 0 ? "Cortesía" : dinero(p.precio)}</span>
            <button data-agregar="${p.id}">Agregar</button>
        </div>`).join("");
    pintarCarrito();
}

const productoPorId = (id) => productos.find((p) => p.id === id);

// Si ya hay una línea del producto sin nota se suma ahí; si la que existe tiene nota se crea otra línea
$("#menu").addEventListener("click", (evento) => {
    const id = Number(evento.target.dataset.agregar);
    if (!id) return;
    const linea = carrito.find((l) => l.producto_id === id && !l.notas.trim());
    linea ? linea.cantidad++ : carrito.push({ producto_id: id, cantidad: 1, notas: "" });
    pintarCarrito();
});

$("#carrito").addEventListener("click", (evento) => {
    const { linea, cambio } = evento.target.dataset;
    if (linea === undefined || cambio === undefined) return;
    carrito[linea].cantidad += Number(cambio);
    if (carrito[linea].cantidad <= 0) carrito.splice(linea, 1);
    pintarCarrito();
});

// La nota se guarda al escribir sin volver a pintar, para no perder el cursor
$("#carrito").addEventListener("input", (evento) => {
    const { nota } = evento.target.dataset;
    if (nota !== undefined) carrito[nota].notas = evento.target.value;
});

const totalCarrito = () => carrito.reduce((total, l) => total + productoPorId(l.producto_id).precio * l.cantidad, 0);

function pintarCarrito() {
    carrito = carrito.filter((l) => productoPorId(l.producto_id));
    const lineas = carrito.map((l, i) => {
        const producto = productoPorId(l.producto_id);
        return `
            <li>
                <div class="linea">
                    <span>${esc(producto.nombre)}</span>
                    <span class="controles">
                        <button class="mini secundario" data-linea="${i}" data-cambio="-1">−</button>
                        ${l.cantidad}
                        <button class="mini secundario" data-linea="${i}" data-cambio="1">+</button>
                        <span>${dinero(producto.precio * l.cantidad)}</span>
                    </span>
                </div>
                <input class="nota" data-nota="${i}" maxlength="100" placeholder="Nota (ej. sin azúcar, extra caliente)" value="${esc(l.notas)}">
            </li>`;
    });
    $("#carrito").innerHTML = lineas.join("") || '<li class="tenue">Agrega productos del menú</li>';
    $("#total").textContent = dinero(totalCarrito());
    actualizarCambio();
}

function actualizarCambio() {
    const efectivo = $("#metodo-pago").value === "efectivo";
    $("#campo-monto").classList.toggle("oculto", !efectivo);
    const recibido = Number($("#monto-recibido").value);
    $("#cambio").textContent = efectivo && recibido ? `Cambio: ${dinero(recibido - totalCarrito())}` : "";
}

$("#metodo-pago").addEventListener("change", actualizarCambio);
$("#monto-recibido").addEventListener("input", actualizarCambio);

$("#btn-registrar").addEventListener("click", () => ejecutar(async () => {
    if (carrito.length === 0) throw new Error("El pedido no tiene productos.");
    const metodo = $("#metodo-pago").value;
    const monto = $("#monto-recibido").value;
    const pedido = await api("/pedidos", {
        method: "POST",
        json: {
            cliente: $("#cliente").value || null,
            metodo_pago: metodo,
            monto_recibido: metodo === "efectivo" && monto !== "" ? Number(monto) : null,
            items: carrito.map((l) => ({ producto_id: l.producto_id, cantidad: l.cantidad, notas: l.notas.trim() || null })),
        },
    });
    carrito = [];
    $("#cliente").value = "";
    $("#monto-recibido").value = "";
    pintarCarrito();
    avisar(`Pedido #${pedido.id} registrado. Total ${dinero(pedido.total)}, cambio ${dinero(pedido.cambio)}.`);
}));

// Pedidos
async function cargarPedidos() {
    const estado = $("#filtro-estado").value;
    const pedidos = await api(`/pedidos${estado ? `?estado=${estado}` : ""}`);
    $("#tabla-pedidos").innerHTML = pedidos.map((p) => `
        <tr>
            <td>${p.id}</td>
            <td>${fecha(p.fecha)}</td>
            <td>${esc(p.cliente) || "—"}</td>
            <td>${p.detalles.map((d) => `${d.cantidad}× ${esc(d.producto.nombre)}${d.notas ? ` <span class="tenue">(${esc(d.notas)})</span>` : ""}`).join("<br>")}</td>
            <td>${dinero(p.total)}</td>
            <td>${p.metodo_pago}</td>
            <td><span class="etiqueta ${p.estado}">${p.estado.replace("_", " ")}</span></td>
            <td>${accionesPedido(p)}</td>
        </tr>`).join("") || '<tr><td colspan="8" class="tenue">Sin pedidos</td></tr>';
}

function accionesPedido(pedido) {
    const botones = [];
    if (pedido.estado === "pendiente") {
        botones.push(`<button class="mini" data-pedido="${pedido.id}" data-estado="en_preparacion">Preparar</button>`);
        if (esAdmin()) botones.push(`<button class="mini peligro" data-cancelar="${pedido.id}">Cancelar</button>`);
    }
    if (pedido.estado === "en_preparacion") {
        botones.push(`<button class="mini" data-pedido="${pedido.id}" data-estado="entregado">Entregar</button>`);
    }
    return botones.join("");
}

$("#filtro-estado").addEventListener("change", () => ejecutar(cargarPedidos));

$("#tabla-pedidos").addEventListener("click", (evento) => ejecutar(async () => {
    const { pedido, estado, cancelar } = evento.target.dataset;
    if (pedido) {
        await api(`/pedidos/${pedido}/estado`, { method: "PATCH", json: { estado } });
        avisar(`Pedido #${pedido} actualizado.`);
    } else if (cancelar) {
        const motivo = await pedir("Motivo de la cancelación:");
        if (motivo === null) return;
        await api(`/pedidos/${cancelar}/cancelar`, { method: "POST", json: { motivo } });
        avisar(`Pedido #${cancelar} cancelado. Los insumos regresaron al inventario.`);
    } else {
        return;
    }
    await cargarPedidos();
}));

// Inventario
async function cargarInventario() {
    const insumos = await api("/inventario/insumos?solo_activos=false");
    $("#tabla-insumos").innerHTML = insumos.map((i) => `
        <tr>
            <td>${esc(i.nombre)}${i.activo ? "" : ' <span class="tenue">(inactivo)</span>'}</td>
            <td>${i.stock} ${i.unidad}</td>
            <td>${i.stock_minimo} ${i.unidad}</td>
            <td><span class="etiqueta ${i.stock_bajo ? "bajo" : "ok"}">${i.stock_bajo ? "Stock bajo" : "Suficiente"}</span></td>
            <td class="solo-admin">
                <button class="mini" data-insumo="${i.id}" data-tipo="entradas">+ Entrada</button>
                <button class="mini secundario" data-insumo="${i.id}" data-tipo="mermas">Merma</button>
            </td>
        </tr>`).join("");

    if (!esAdmin()) return;
    const movimientos = await api("/inventario/movimientos?limite=20");
    $("#tabla-movimientos").innerHTML = movimientos.map((m) => `
        <tr>
            <td>${fecha(m.fecha)}</td>
            <td>${esc(m.insumo.nombre)}</td>
            <td>${m.tipo}</td>
            <td>${m.cantidad > 0 ? "+" : ""}${m.cantidad} ${m.insumo.unidad}</td>
            <td>${m.stock_resultante}</td>
            <td>${esc(m.motivo)}</td>
        </tr>`).join("");
}

$("#tabla-insumos").addEventListener("click", (evento) => ejecutar(async () => {
    const { insumo, tipo } = evento.target.dataset;
    if (!insumo) return;
    const cantidad = await pedir(tipo === "entradas" ? "Cantidad que entra al inventario:" : "Cantidad perdida (merma):");
    if (cantidad === null) return;
    const motivo = await pedir("Motivo:", tipo === "entradas" ? "Compra a proveedor" : "");
    if (motivo === null) return;
    await api(`/inventario/insumos/${insumo}/${tipo}`, {
        method: "POST",
        json: { cantidad: Number(cantidad), motivo: motivo || null },
    });
    avisar("Movimiento registrado.");
    await cargarInventario();
}));

// Productos
async function cargarProductos() {
    const lista = await api("/productos?solo_activos=false");
    $("#tabla-productos").innerHTML = lista.map((p) => `
        <tr>
            <td>${esc(p.nombre)}</td>
            <td>${p.categoria.replace("_", " ")}</td>
            <td>${dinero(p.precio)}</td>
            <td class="pequeno">${p.receta.map((r) => `${r.cantidad} ${r.insumo.unidad} ${esc(r.insumo.nombre)}`).join("<br>")}</td>
            <td><span class="etiqueta ${p.activo ? "ok" : "cancelado"}">${p.activo ? "Activo" : "Inactivo"}</span></td>
            <td>
                <button class="mini" data-precio="${p.id}">Precio</button>
                <button class="mini secundario" data-activar="${p.id}" data-valor="${!p.activo}">${p.activo ? "Desactivar" : "Activar"}</button>
            </td>
        </tr>`).join("");
}

$("#tabla-productos").addEventListener("click", (evento) => ejecutar(async () => {
    const { precio, activar, valor } = evento.target.dataset;
    if (precio) {
        const nuevo = await pedir("Nuevo precio (puede ser 0):");
        if (nuevo === null) return;
        await api(`/productos/${precio}`, { method: "PUT", json: { precio: Number(nuevo) } });
    } else if (activar) {
        await api(`/productos/${activar}`, { method: "PUT", json: { activo: valor === "true" } });
    } else {
        return;
    }
    avisar("Producto actualizado.");
    await cargarProductos();
}));

// Usuarios
async function cargarUsuarios() {
    const usuarios = await api("/usuarios");
    $("#tabla-usuarios").innerHTML = usuarios.map((u) => `
        <tr>
            <td>${esc(u.nombre)}</td>
            <td>${esc(u.usuario)}</td>
            <td>${u.rol}</td>
            <td><span class="etiqueta ${u.activo ? "ok" : "cancelado"}">${u.activo ? "Activo" : "Inactivo"}</span></td>
            <td>${u.id === sesion.usuario.id ? "" : `<button class="mini secundario" data-activar="${u.id}" data-valor="${!u.activo}">${u.activo ? "Desactivar" : "Activar"}</button>`}</td>
        </tr>`).join("");
}

$("#form-usuario").addEventListener("submit", (evento) => {
    evento.preventDefault();
    ejecutar(async () => {
        const datos = new FormData(evento.target);
        const usuario = await api("/usuarios", {
            method: "POST",
            json: { nombre: datos.get("nombre"), usuario: datos.get("usuario"), password: datos.get("password"), rol: "cajero" },
        });
        evento.target.reset();
        avisar(`Cajero '${usuario.usuario}' registrado.`);
        await cargarUsuarios();
    });
});

$("#tabla-usuarios").addEventListener("click", (evento) => ejecutar(async () => {
    const { activar, valor } = evento.target.dataset;
    if (!activar) return;
    await api(`/usuarios/${activar}`, { method: "PUT", json: { activo: valor === "true" } });
    avisar("Usuario actualizado.");
    await cargarUsuarios();
}));

// Reportes
async function cargarReportes() {
    const filtros = new URLSearchParams();
    if ($("#fecha-inicio").value) filtros.set("fecha_inicio", $("#fecha-inicio").value);
    if ($("#fecha-fin").value) filtros.set("fecha_fin", $("#fecha-fin").value);

    const [ventas, top, stockBajo] = await Promise.all([
        api(`/reportes/ventas?${filtros}`),
        api(`/reportes/productos-mas-vendidos?${filtros}`),
        api("/reportes/stock-bajo"),
    ]);

    const tarjeta = (titulo, valor) => `<div class="tarjeta"><span class="tenue">${titulo}</span><strong>${valor}</strong></div>`;
    $("#resumen-ventas").innerHTML = [
        tarjeta("Total vendido", dinero(ventas.total_vendido)),
        tarjeta("Pedidos", ventas.numero_pedidos),
        tarjeta("Ticket promedio", dinero(ventas.ticket_promedio)),
        tarjeta("Efectivo", dinero(ventas.por_metodo_pago.efectivo.total)),
        tarjeta("Tarjeta", dinero(ventas.por_metodo_pago.tarjeta.total)),
        tarjeta("Cancelados", ventas.pedidos_cancelados),
    ].join("");

    $("#tabla-top").innerHTML = top.map((p) => `
        <tr><td>${esc(p.nombre)}</td><td>${p.unidades_vendidas}</td><td>${dinero(p.importe)}</td></tr>`).join("")
        || '<tr><td colspan="3" class="tenue">Sin ventas en el periodo</td></tr>';

    $("#lista-stock-bajo").innerHTML = stockBajo.map((i) => `
        <li>${esc(i.nombre)}: ${i.stock} ${i.unidad} (mínimo ${i.stock_minimo})</li>`).join("")
        || '<li class="tenue">Todos los insumos tienen stock suficiente</li>';
}

$("#btn-reporte").addEventListener("click", () => ejecutar(cargarReportes));

// Inicio
sesion.token ? mostrarApp() : cerrarSesion();
