import reflex as rx
from src.components.Cart.cart_item import CartItem
from src.components.Cart.cart_info import CartInfo

# state
from src.state import CartState


def Cart() -> rx.Component:
    return rx.chakra.box(
        rx.chakra.box(
            rx.chakra.box(
                rx.chakra.text("Total Amount: "),
                rx.chakra.text("₹ ", CartState.total),
                class_name="flex justify-between mx-4 my-2 font-semibold text-xl",
            ),
            rx.chakra.box(
                rx.chakra.button(
                    "i",
                    on_click=CartState.toggle_info,
                    class_name="flex justify-center items-center w-11 h-11 border-2 text-accent transition-colors border-accent hover:bg-accent hover:text-white rounded-full font-black shadow",
                    background="auto",
                    _hover={"background": "auto"},
                    border_radius="50%",
                ),
                rx.chakra.button(
                    "CHECKOUT",
                    on_click=CartState.toggle_info,
                    background="auto",
                    _hover={"background": "auto"},
                    class_name="grow bg-primary hover:bg-primary-450 transition-colors ml-2 py-2 rounded text-white shadow",
                ),
                class_name="flex mx-4 my-2 font-bold text-2xl items-center",
            ),
            class_name="CartBtn",
        ),
        rx.chakra.divider(),
        rx.chakra.box(
            rx.foreach(CartState.cart, lambda item: CartItem(item)),
            class_name=rx.cond(
                CartState.show_info,
                "CartInfo overflow-y-scroll px-2 Active",
                "CartInfo overflow-y-scroll px-2",
            ),
        ),
        rx.chakra.box(
            rx.foreach(CartState.cart, lambda item: CartInfo(item)),
            class_name=rx.cond(
                CartState.show_info,
                "CartList overflow-y-scroll px-2",
                "CartList overflow-y-scroll px-2 Active",
            ),
        ),
        class_name=rx.cond(
            CartState.show_cart,
            "Cart flex flex-col-reverse relative bg-white rounded-lg mr-2 shadow max-h-full right-0 bottom-0 sm:min-w-auto min-w-max h-full Active",
            "Cart flex flex-col-reverse relative bg-white rounded-lg mr-2 shadow max-h-full right-0 bottom-0 sm:min-w-auto min-w-max h-full",
        ),
    )
