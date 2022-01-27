
addon_name = 'ets_cds'


spisok = []
# spisok.append(['adbook.branch','', 1])
spisok.append(['cds.department'])
spisok.append(['cds.location'])
spisok.append(['cds.object_type'])
spisok.append(['cds.object_class'])
spisok.append(['cds.energy_complex'])
spisok.append(['cds.energy_complex_matching'])
spisok.append(['cds.energy_complex_object'])
spisok.append(['cds.request'])
spisok.append(['cds.request_matching'])


print("id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink")

#  group_cds_read_only Может просматривать заявки и справочники
group_name = 'group_cds_read_only'
spisok = []
spisok.append(['cds.department', '1,0,0,0'])
spisok.append(['cds.location', '1,0,0,0'])
spisok.append(['cds.object_type', '1,0,0,0'])
spisok.append(['cds.object_class', '1,0,0,0'])
spisok.append(['cds.energy_complex', '1,0,0,0'])
spisok.append(['cds.energy_complex_matching', '1,0,0,0'])
spisok.append(['cds.energy_complex_object', '1,0,0,0'])
spisok.append(['cds.request', '1,0,0,0'])
spisok.append(['cds.request_matching', '1,0,0,0'])

for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name)>1:
		access = name[1]
	else:
		access = '0,0,0,0'

	print('access_%(class_name)s_%(group_name)s,%(name)s,%(modul_name)smodel_%(class_name)s,%(addon_name)s.%(group_name)s,%(access)s' % {'name':name[0], 'class_name': class_name, 'group_name': group_name, 'access': access, 'modul_name': modul_name, 'addon_name': addon_name})




#  group_cds_executor Формирующий и подающий заявку работник.

group_name = 'group_cds_executor'
spisok = []
spisok.append(['cds.department', '1,0,0,0'])
spisok.append(['cds.location', '1,0,0,0'])
spisok.append(['cds.object_type', '1,0,0,0'])
spisok.append(['cds.object_class', '1,0,0,0'])
spisok.append(['cds.energy_complex', '1,1,0,0'])
spisok.append(['cds.energy_complex_matching', '1,1,1,0'])
spisok.append(['cds.energy_complex_object', '1,1,0,0'])
spisok.append(['cds.request', '1,1,1,0'])
spisok.append(['cds.request_matching', '1,1,1,0'])

for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name)>1:
		access = name[1]
	else:
		access = '0,0,0,0'

	print('access_%(class_name)s_%(group_name)s,%(name)s,%(modul_name)smodel_%(class_name)s,%(addon_name)s.%(group_name)s,%(access)s' % {'name':name[0], 'class_name': class_name, 'group_name': group_name, 'access': access, 'modul_name': modul_name, 'addon_name': addon_name})



#  group_cds_dispetcher Может создавать заявки, справочнки, согласовывать заявки

group_name = 'group_cds_dispetcher'
spisok = []
spisok.append(['cds.department', '1,1,1,0'])
spisok.append(['cds.location', '1,1,1,0'])
spisok.append(['cds.object_type', '1,1,1,0'])
spisok.append(['cds.object_class', '1,1,1,0'])
spisok.append(['cds.energy_complex', '1,1,1,0'])
spisok.append(['cds.energy_complex_matching', '1,1,1,0'])
spisok.append(['cds.energy_complex_object', '1,1,1,0'])
spisok.append(['cds.request', '1,1,1,0'])
spisok.append(['cds.request_matching', '1,1,1,0'])

for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name)>1:
		access = name[1]
	else:
		access = '0,0,0,0'

	print('access_%(class_name)s_%(group_name)s,%(name)s,%(modul_name)smodel_%(class_name)s,%(addon_name)s.%(group_name)s,%(access)s' % {'name':name[0], 'class_name': class_name, 'group_name': group_name, 'access': access, 'modul_name': modul_name, 'addon_name': addon_name})



#  group_cds_edit_directory Может редактировать справочнки

group_name = 'group_cds_edit_directory'
spisok = []
spisok.append(['cds.department', '1,1,1,0'])
spisok.append(['cds.location', '1,1,1,0'])
spisok.append(['cds.object_type', '1,1,1,0'])
spisok.append(['cds.object_class', '1,1,1,0'])
spisok.append(['cds.energy_complex', '1,1,1,0'])
spisok.append(['cds.energy_complex_matching', '1,1,1,0'])
spisok.append(['cds.energy_complex_object', '1,1,1,0'])

for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name)>1:
		access = name[1]
	else:
		access = '0,0,0,0'

	print('access_%(class_name)s_%(group_name)s,%(name)s,%(modul_name)smodel_%(class_name)s,%(addon_name)s.%(group_name)s,%(access)s' % {'name':name[0], 'class_name': class_name, 'group_name': group_name, 'access': access, 'modul_name': modul_name, 'addon_name': addon_name})



#  group_cds_admin Полный доступ, создание, редактирование, удаление

group_name = 'group_cds_admin'
spisok = []
spisok.append(['cds.department', '1,1,1,1'])
spisok.append(['cds.location', '1,1,1,1'])
spisok.append(['cds.object_type', '1,1,1,1'])
spisok.append(['cds.object_class', '1,1,1,1'])
spisok.append(['cds.energy_complex', '1,1,1,1'])
spisok.append(['cds.energy_complex_matching', '1,1,1,1'])
spisok.append(['cds.energy_complex_object', '1,1,1,1'])
spisok.append(['cds.request', '1,1,1,1'])
spisok.append(['cds.request_matching', '1,1,1,1'])

for name in spisok:
	class_name = name[0].replace('.','_')
	modul_name = ''
	
	if len(name)>1:
		access = name[1]
	else:
		access = '0,0,0,0'

	print('access_%(class_name)s_%(group_name)s,%(name)s,%(modul_name)smodel_%(class_name)s,%(addon_name)s.%(group_name)s,%(access)s' % {'name':name[0], 'class_name': class_name, 'group_name': group_name, 'access': access, 'modul_name': modul_name, 'addon_name': addon_name})