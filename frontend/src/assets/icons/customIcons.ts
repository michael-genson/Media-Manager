import { h } from "vue";
import type { IconSet, IconProps } from "vuetify";
import logo from "./data/LogoIcon.vue";

const customIconNameToComponent: any = {
    logo,
};

const customIcons: IconSet = {
    // @ts-ignore
    component: (props: IconProps) => h(customIconNameToComponent[props.icon]),
};

export { customIcons };
