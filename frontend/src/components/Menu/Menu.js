import React, { useEffect } from "react";
import MenuItem from "./MenuItem";
import useMenuContext from "../../hooks/useMenuContext";
import useUserContext from "../../hooks/useUserContext";
import { getMenu } from "../../controllers/menuController";

const Menu = React.memo(() => {
  const { menu, dispatch } = useMenuContext();
  const { user } = useUserContext();
  useEffect(() => {
    getMenu(user.token)
      .then((data) => {
        data.forEach((element) => {
          element.selected = false;
        });
        dispatch({ type: "SET_MENU", payload: data });
      })
      .catch((err) => {
        console.log(err);
      });
  }, [user.token, dispatch]);

  return (
    <div className="Menu grow px-2 overflow-y-auto">
      <div className="flex flex-wrap justify-evenly overflow-y-scroll">
        {menu &&
          menu.map((item) => (
            <MenuItem
              key={item.item_id}
              id={item.item_id}
              img={item.item_icon || "chicken-noodles.jpg"}
              name={item.item_name}
              price={item.item_price}
              quantity={item.item_quantity}
              type={item.item_type}
              selected={item.selected}
            />
          ))}
      </div>
    </div>
  );
});

export default Menu;
