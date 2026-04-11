import flet as ft
from insertion_view import InsertionView
from avl_panel import PanelAVL
from concurrency_panel import PanelConcurrency
from stress_panel import PanelStress
from create_flight import PanelForms
from modify_flight import ModifyPanel
from create_flight_stress import StressForms
from update_flight_stress import UpdatePanelStress
from compare_view import build_compare_view
from metodos_vuelos import middleware

def main(page: ft.Page):
    page.title = "Menú Principal"

    print("Initial route:", page.route)

    async def open_insertion(e):
        await page.push_route("/insertion")

    async def open_panel_avl(e):
        await page.push_route("/panelavl")

    async def open_panel_concurrency(e):
        await page.push_route("/concurrencypanel")
    
    async def open_panel_stress(e):
        print(middleware.set_stress_mode(True))
        await page.push_route("/stresspanel")

    async def open_panel_draw(e):
        await page.push_route("/drawpanel")
        

    def route_change():
        print("Route change:", page.route)
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                padding=0,
                spacing=0,
                controls=[
                    ft.Container(
                        expand=True, # Ocupa todo el alto y ancho
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.BOTTOM_CENTER,
                            end=ft.Alignment.TOP_CENTER,
                            colors=[ft.Colors.GREY, ft.Colors.LIGHT_BLUE]),
                            alignment=ft.Alignment.CENTER,
                        content =
                            ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=30,
                                controls = [
                                    ft.Container(
                                        content=ft.Text(
                                            "Sistema de Gestión de Vuelos", 
                                            size=30, 
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        margin=ft.Margin.only(bottom=100),
                                    ),
                                    ft.Button("Modos de Inserción", width = 200, height = 50, on_click=open_insertion),
                                    ft.Button("Panel AVL de Vuelos", width = 200, height = 50, on_click=open_panel_avl),
                                    ft.Button("Panel de Concurrencia", width = 200, height = 50, on_click=open_panel_concurrency),
                                    ft.Button("Panel Modo Estres", width = 200, height = 50, on_click=open_panel_stress),
                                    ft.Button("Panel de Graficas", width = 200, height = 50, on_click=open_panel_draw)
                                ]
                            )
                    )
                ],
            )
        )

        if page.route == "/insertion":
            page.views.append(
                InsertionView(page)
            )
        if page.route == "/panelavl":
            page.views.append(
                PanelAVL(page)
            )
        if page.route == "/concurrencypanel":
            page.views.append(
                PanelConcurrency(page)
            )
        if page.route == "/stresspanel":
            page.views.append(
                PanelStress(page)
            )

        if page.route == "/formpanel":
            page.views.append(
                PanelForms(page)
            )
        
        if page.route == "/modifypanel":
            page.views.append(
                ModifyPanel(page)
            )

        if page.route == "/stressform":
            page.views.append(
                StressForms(page)
            )
        
        if page.route == "/updateflightstress":
            page.views.append(
                UpdatePanelStress(page)
            )

        if page.route == "/drawpanel":
            page.views.append(
                build_compare_view(page)
            )
        page.update()
        
    async def view_pop(e):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()


if __name__ == "__main__":
    ft.run(main)